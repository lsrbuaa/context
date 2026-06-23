# 记忆层存储技术选型

## 概述

本文档为七层记忆架构的每一层推荐具体存储技术方案，区分端侧和云侧实现，并说明选型理由、性能预期和替代方案。

---

## 1. 选型总表

| 层 | 数据形态 | 核心查询模式 | 推荐方案(端侧) | 推荐方案(云侧) | 选型理由 |
|----|----------|-------------|---------------|---------------|----------|
| **L1** Raw Buffer | 连续字节流 | 时序回放/覆盖 | Ring Buffer (RAM) | N/A (不上云) | 极低延迟, 隐私不出端 |
| **L2** Perception WM | 结构化 JSON (单条) | 全量读写 | In-memory struct | N/A | 实时更新, 只存当前状态 |
| **L3** Task WM | 结构化状态 + 历史 | 全量读 + 追加写 | SQLite (WAL mode) | N/A | 任务切换时需持久化 |
| **L4** Episodic | 事件记录 + embeddings | 向量相似 + 时间范围 + 空间 | **SQLite + sqlite-vss** | **Qdrant / Weaviate** | 混合检索(向量+过滤) |
| **L5** Semantic | 实体 + 关系 + 属性 | 图遍历 + 属性查询 | **SQLite (关系表)** | **Neo4j / Graphiti** | 关系型查询为主 |
| **L6** Procedural | if-then 规则 | 条件匹配 + 优先级 | **JSON 文件 + 内存索引** | 同步备份 | 规则数少(<500), 需快速匹配 |
| **L7** Governance | 元数据(附属) | 主键关联查询 | 与 L4-L6 同库(额外列) | 与 L4-L6 同库 | 避免多库同步开销 |

---

## 2. 各层详细方案

### 2.1 L1: Raw Sensor Buffer

**需求:**
- 持续写入原始传感器数据 (音频 32-96 KB/s, 视频帧 ~170 KB/帧)
- 保留最近 30s-60s，自动覆盖旧数据
- 绝对不持久化到磁盘（隐私要求）
- 需要偶尔回放（当事件被标记为重要时回溯）

**方案: 环形缓冲区 (Ring Buffer in RAM)**

```c
// 概念实现
struct RingBuffer {
    uint8_t* data;          // 预分配内存块
    size_t capacity;        // 总容量 (e.g., 50MB)
    size_t write_pos;       // 当前写入位置
    size_t read_pos;        // 最旧有效数据位置
    uint64_t timestamp_start; // 最旧数据时间戳
};

// 音频 buffer: 16kHz × 16bit × 60s = 1.92 MB
// 视频关键帧 buffer: 170KB × 2fps × 30s = 10.2 MB
// 总 RAM 占用: ~15-50 MB
```

| 维度 | 规格 |
|------|------|
| 存储介质 | RAM (不落盘) |
| 容量 | 15-50 MB (按设备类型) |
| 写入延迟 | <1μs (内存拷贝) |
| 读取延迟 | <1μs |
| 覆盖策略 | FIFO 环形覆盖 |
| 持久化 | 永不 (设备重启即清空) |
| 加密 | 不需要 (RAM 中, 短暂) |

---

### 2.2 L2: Perception Working Memory

**需求:**
- 存储当前场景的结构化表示 (1 条 JSON, ~2KB)
- 高频更新 (每秒多次)
- 只保留最新状态，无需历史
- 读取极快 (Context Compiler 每次都要读)

**方案: 内存结构体 / In-memory JSON**

```python
# 概念实现 (Python/端侧框架)
class PerceptionWM:
    current_scene: dict       # 当前场景 JSON
    last_updated: datetime    # 最后更新时间
    change_flags: dict        # 变化标记
    
    def update(self, new_perception: dict):
        self.change_flags = diff(self.current_scene, new_perception)
        self.current_scene = new_perception
        self.last_updated = now()
```

| 维度 | 规格 |
|------|------|
| 存储介质 | RAM (进程内存) |
| 数据量 | ~2-5 KB |
| 更新延迟 | <0.1ms |
| 读取延迟 | <0.01ms |
| 持久化 | 不需要 (场景切换即重建) |

---

### 2.3 L3: Task Working Memory

**需求:**
- 存储当前任务状态 + 短期历史 (对话轮次, 任务步骤)
- 任务切换时需要归档/恢复
- Context Compiler 每次调用模型前读取
- 偶尔需要回滚到之前的状态

**方案: SQLite (WAL mode) / 端侧轻量数据库**

```sql
-- Schema
CREATE TABLE task_state (
    task_id TEXT PRIMARY KEY,
    status TEXT,  -- active / paused / completed
    state_json TEXT,  -- 完整任务状态 JSON
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    event_type TEXT,  -- state_change / user_message / tool_result
    content TEXT,
    timestamp DATETIME
);
```

| 维度 | 规格 |
|------|------|
| 存储介质 | 端侧 Flash (SQLite) |
| 数据量 | ~100 KB - 1 MB |
| 写入延迟 | ~1ms (WAL mode) |
| 读取延迟 | <1ms |
| 持久化 | 是 (任务可中断恢复) |
| 保留策略 | 活跃任务常驻, 完成任务归档到 L4 |

---

### 2.4 L4: Episodic Memory (核心层)

**需求:**
- 存储数万条事件记录 (10K-50K)
- 每条含文本 + embedding 向量 (512-1536d)
- 检索模式: 向量相似度 + 时间范围 + 地点过滤 + 人物过滤
- 支持 Top-K 检索 (Context Ranker 用)
- 需要时间衰减 (权重随时间降低)

**方案: 端侧 SQLite + sqlite-vss / 云侧 Vector DB**

#### 端侧方案: SQLite + sqlite-vss

```sql
-- Schema
CREATE TABLE episodes (
    memory_id TEXT PRIMARY KEY,
    summary TEXT NOT NULL,
    full_content TEXT,
    importance_score REAL,
    confidence REAL,
    
    -- 时间
    event_time DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    last_accessed DATETIME,
    access_count INTEGER DEFAULT 0,
    
    -- 上下文过滤字段
    location TEXT,
    location_type TEXT,
    activity_type TEXT,
    people TEXT,  -- JSON array of person_ids
    
    -- 隐私治理 (L7 内嵌)
    privacy_level TEXT DEFAULT 'private',
    source TEXT,
    expires_at DATETIME,
    user_verified BOOLEAN DEFAULT 0,
    
    -- 向量 (sqlite-vss 虚拟表关联)
    embedding BLOB  -- 512d float32 = 2KB
);

-- 向量索引 (sqlite-vss)
CREATE VIRTUAL TABLE episode_vectors USING vss0(
    embedding(512)
);

-- 常用查询索引
CREATE INDEX idx_time ON episodes(event_time DESC);
CREATE INDEX idx_location ON episodes(location_type);
CREATE INDEX idx_people ON episodes(people);
CREATE INDEX idx_importance ON episodes(importance_score DESC);
```

#### 检索策略: 混合查询

```python
def retrieve_episodes(query_embedding, filters, top_k=10):
    # Step 1: 预过滤 (SQL, <1ms)
    candidates = sql_query("""
        SELECT memory_id FROM episodes
        WHERE event_time > ? 
        AND (location_type = ? OR ? IS NULL)
        AND importance_score > 0.3
        AND privacy_level != 'sensitive'
        LIMIT 200
    """, [time_threshold, location_filter])
    
    # Step 2: 向量排序 (sqlite-vss, ~5-20ms for 200 candidates)
    results = vss_search(query_embedding, candidates, top_k)
    
    # Step 3: Context Ranker 重排 (~2ms)
    ranked = context_ranker.score(results, current_context)
    
    return ranked[:top_k]
```

#### 云侧方案: Qdrant / Weaviate

| 维度 | Qdrant | Weaviate |
|------|--------|----------|
| 向量检索 | HNSW, 快速 | HNSW, 快速 |
| 元数据过滤 | Payload filter | GraphQL filter |
| 时间查询 | 支持 | 支持 |
| 多租户 | 支持 | 支持 |
| 部署 | Docker / Cloud | Docker / Cloud |

#### 性能预期

| 操作 | 端侧 (SQLite+vss, 10K条) | 云侧 (Qdrant, 50K条) |
|------|--------------------------|---------------------|
| 单条写入 | ~2ms | ~5ms + 网络 |
| Top-10 向量检索 | ~20ms | ~10ms + 30ms网络 |
| 混合过滤+检索 | ~25ms | ~15ms + 30ms网络 |
| 全量扫描 | ~50ms | ~30ms + 30ms网络 |

---

### 2.5 L5: Semantic Memory

**需求:**
- 存储实体(人物/地点/概念)及其关系 (1K-5K 条)
- 查询模式: "张工的部门是什么?" / "谁是技术部的?" / "用户常去的地方?"
- 支持关系遍历 (人物→部门→同事)
- 支持属性更新 (某人新增一个话题标签)
- 需要双向索引 (Phase 1 Reversal Curse 约束)

**方案: 端侧 SQLite 关系表 / 云侧 Neo4j 或 Graphiti**

#### 端侧方案: SQLite 关系型

```sql
-- 实体表
CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT,  -- person / place / concept / object
    name TEXT,
    properties TEXT,  -- JSON (灵活属性)
    created_at DATETIME,
    updated_at DATETIME,
    confidence REAL,
    derived_from TEXT  -- JSON array of episode_ids
);

-- 关系表 (支持双向查询)
CREATE TABLE relations (
    id INTEGER PRIMARY KEY,
    subject_id TEXT,
    predicate TEXT,  -- "is_colleague_of" / "located_in" / "prefers"
    object_id TEXT,
    confidence REAL,
    first_observed DATETIME,
    last_confirmed DATETIME,
    observation_count INTEGER DEFAULT 1,
    
    FOREIGN KEY (subject_id) REFERENCES entities(entity_id),
    FOREIGN KEY (object_id) REFERENCES entities(entity_id)
);

-- 双向索引 (解决 Reversal Curse)
CREATE INDEX idx_rel_subject ON relations(subject_id, predicate);
CREATE INDEX idx_rel_object ON relations(object_id, predicate);
CREATE INDEX idx_rel_predicate ON relations(predicate);
```

#### 查询示例

```sql
-- 正向: "张工的同事有谁?"
SELECT e.name FROM relations r
JOIN entities e ON r.object_id = e.entity_id
WHERE r.subject_id = 'contact_zhang' AND r.predicate = 'is_colleague_of';

-- 反向: "谁是张工的同事?" (同一查询，因为双向索引)
SELECT e.name FROM relations r
JOIN entities e ON r.subject_id = e.entity_id
WHERE r.object_id = 'contact_zhang' AND r.predicate = 'is_colleague_of';

-- 多跳: "张工部门里还有谁?"
SELECT e.name FROM relations r1
JOIN relations r2 ON r1.object_id = r2.subject_id
JOIN entities e ON r2.object_id = e.entity_id
WHERE r1.subject_id = 'contact_zhang' 
AND r1.predicate = 'belongs_to_dept'
AND r2.predicate = 'has_member';
```

#### 云侧方案: Neo4j / Graphiti

适合当实体规模 >5K 或关系复杂度高时：

```cypher
// Neo4j 示例
MATCH (u:Person {name: "张工"})-[:COLLEAGUE_OF]->(c:Person)
RETURN c.name, c.department

// 多跳
MATCH (u:Person {name: "张工"})-[:BELONGS_TO]->(d:Department)<-[:BELONGS_TO]-(c:Person)
WHERE c <> u
RETURN c.name
```

| 维度 | 端侧 SQLite | 云侧 Neo4j |
|------|-------------|------------|
| 适用规模 | <5K 实体 | >5K 实体 |
| 多跳查询 | 需要多次 JOIN (慢) | 原生图遍历 (快) |
| 写入延迟 | <1ms | ~5ms + 网络 |
| 查询延迟 | <5ms (2跳内) | <10ms + 网络 |
| 存储大小 | ~1-5 MB | 云端无限制 |

---

### 2.6 L6: Procedural Memory

**需求:**
- 存储行为规则 (100-500 条)
- 每条规则含: 触发条件 + 动作 + 优先级 + 例外
- 运行时快速匹配: 当前场景是否命中某条规则?
- 规则可动态增删改

**方案: JSON 文件 + 内存哈希索引**

```json
// rules.json
[
  {
    "rule_id": "proc_015",
    "name": "meeting_silent_mode",
    "priority": 90,
    "condition": {
      "operator": "AND",
      "clauses": [
        {"field": "location_type", "op": "in", "value": ["meeting_room"]},
        {"field": "activity", "op": "eq", "value": "meeting"},
        {"field": "calendar_event_active", "op": "eq", "value": true}
      ]
    },
    "action": {
      "set_output_mode": "haptic_only",
      "suppress_notifications": true,
      "record_mode": "meeting_summary"
    },
    "exceptions": [
      {"field": "alert_level", "op": "eq", "value": "emergency"}
    ],
    "metadata": {
      "source": "user_explicit",
      "created_at": "2026-06-10",
      "trigger_count": 18,
      "success_rate": 0.94
    }
  }
]
```

#### 匹配引擎

```python
class RuleEngine:
    def __init__(self, rules_path: str):
        self.rules = load_json(rules_path)
        # 按条件字段建立倒排索引
        self.index = build_field_index(self.rules)
    
    def match(self, context: dict) -> list[Rule]:
        """返回当前 context 命中的所有规则，按优先级排序"""
        candidates = self.index.lookup(context)  # O(1) 哈希查找
        matched = [r for r in candidates if r.evaluate(context)]
        return sorted(matched, key=lambda r: r.priority, reverse=True)
```

| 维度 | 规格 |
|------|------|
| 存储 | JSON 文件 (端侧 Flash) |
| 运行时 | 内存加载 + 哈希索引 |
| 匹配延迟 | <1ms (500 条规则) |
| 存储大小 | ~50-200 KB |
| 同步 | 端云双向同步 (规则变更时) |

---

### 2.7 L7: Governance Memory

**需求:**
- 为 L4-L6 的每条记忆附加元信息
- 包含: 来源、置信度、隐私级别、过期时间、访问日志
- 不独立存储，而是作为主记忆的额外字段

**方案: 嵌入主表 (额外列) + 独立审计日志**

```sql
-- L4 episodes 表已包含 governance 字段 (见 2.4)
-- 额外: 审计日志表 (记录所有访问和修改)

CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    memory_layer TEXT,  -- 'L4' / 'L5' / 'L6'
    action TEXT,  -- 'created' / 'accessed' / 'modified' / 'deleted'
    actor TEXT,  -- 'context_compiler' / 'consolidation_job' / 'user'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT  -- JSON (修改内容/访问原因)
);

CREATE INDEX idx_audit_memory ON audit_log(memory_id, timestamp DESC);
CREATE INDEX idx_audit_time ON audit_log(timestamp DESC);
```

| 维度 | 规格 |
|------|------|
| 存储 | 与主记忆同库 (额外列 + 审计表) |
| 写入开销 | 每次记忆操作 +1 audit_log 行 (~0.5ms) |
| 存储开销 | ~20% overhead on L4-L6 |
| 查询 | 按 memory_id 关联查询 |

---

## 3. 端侧统一存储架构

```
端侧存储布局:
├── RAM (~50-200 MB)
│   ├── L1 Ring Buffer: 15-50 MB
│   ├── L2 Perception WM: 2-5 KB
│   ├── L6 Rule Engine (loaded): ~500 KB
│   └── L4 热缓存 (最近 100 条 embedding): ~1 MB
│
├── Flash/SQLite (~100-200 MB)
│   ├── task_state.db (L3): ~1 MB
│   ├── episodes.db (L4 热数据, 最近 30 天): ~50 MB
│   │   ├── episodes 表 (文本+元数据)
│   │   └── episode_vectors (sqlite-vss 索引)
│   ├── knowledge.db (L5): ~5 MB
│   │   ├── entities 表
│   │   └── relations 表
│   ├── rules.json (L6): ~200 KB
│   └── audit.db (L7): ~10 MB
│
└── 加密存储 (隐私数据)
    └── encrypted_episodes.db (含旁人信息的记忆): ~20 MB
```

---

## 4. 云侧统一存储架构

```
云侧存储布局:
├── Vector DB (Qdrant/Weaviate)
│   └── Collection: user_{id}_episodes
│       ├── 全量 L4 记忆 (含 embedding)
│       ├── Payload: 全部过滤字段
│       └── 容量: ~50K vectors × 512d = ~100 MB
│
├── Graph DB (Neo4j) 或 Document DB
│   └── Database: user_{id}_knowledge
│       ├── 实体节点 + 关系边
│       └── 容量: ~5K nodes, ~10K edges = ~10 MB
│
├── Object Storage (S3/COS)
│   └── Bucket: user_{id}_archive
│       ├── 冷数据 L4 (>90天, 压缩)
│       └── 原始转录备份 (可选)
│
└── Metadata DB (PostgreSQL)
    ├── 用户配置
    ├── 同步状态
    └── 审计日志 (L7 cloud copy)
```

---

## 5. 端云同步策略

| 同步方向 | 触发条件 | 内容 | 策略 |
|----------|----------|------|------|
| 端→云 (上传) | Wi-Fi 连接时 | 新增 L4 记忆 | 增量上传, 加密传输 |
| 端→云 (上传) | 归纳完成时 | L5/L6 更新 | 即时同步 |
| 云→端 (下载) | 设备启动时 | L5/L6 最新版 | 全量覆盖(小数据量) |
| 云→端 (下载) | 按需 | L4 冷数据检索结果 | 仅检索命中的条目 |
| 冲突解决 | 双侧修改同一条 | 任何层 | 时间戳新者优先 + 保留冲突记录 |

---

## 6. 性能 Benchmark 预期

| 操作 | 目标延迟 | 端侧 SQLite | 云侧 |
|------|----------|-------------|------|
| L2 读取 | <0.1ms | ✓ (内存) | N/A |
| L4 写入单条 | <5ms | ~2ms | ~5ms+30ms网络 |
| L4 Top-10 混合检索 | <50ms | ~25ms | ~15ms+30ms网络 |
| L5 单跳关系查询 | <5ms | ~2ms | ~5ms+30ms网络 |
| L5 双跳查询 | <20ms | ~10ms | ~8ms+30ms网络 |
| L6 规则匹配 | <2ms | ~0.5ms | N/A (端侧) |
| L7 审计写入 | <2ms | ~0.5ms | 异步批量 |

**结论: 端侧 SQLite 方案可满足大部分实时性要求。云侧主要用于全量存储和复杂查询。**
