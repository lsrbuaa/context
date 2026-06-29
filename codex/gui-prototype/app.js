const app = document.getElementById("app");
const stage = document.getElementById("stage");
const backButton = document.getElementById("backButton");
const searchInput = document.getElementById("searchInput");
const drawer = document.getElementById("detailDrawer");
const drawerContent = document.getElementById("drawerContent");
const drawerKicker = document.getElementById("drawerKicker");
const drawerClose = document.getElementById("drawerClose");

const state = {
  camera: {
    level: "world",
    buildingId: null,
    roomId: null,
    objectId: null
  },
  intent: "learn",
  userPrompt: "",
  searchQuery: "",
  layers: {
    evidence: false,
    risk: false,
    questions: false
  },
  hoveredBuildingId: null,
  selectedBuildingId: null,
  labelDensity: "minimal",
  motion: "continuity"
};

const asset = (name) => `./assets/generated/${name}`;

const evidenceLibrary = {
  S001: {
    title: "Lost in the Middle",
    strength: "强",
    note: "长上下文会受到位置和注意力分布影响，不能只依赖窗口长度。"
  },
  S002: {
    title: "RAG / Memory / Tool 边界",
    strength: "中",
    note: "不同外部上下文机制承担不同职责，需要显式治理。"
  },
  S003: {
    title: "LangGraph 状态与记忆",
    strength: "强",
    note: "运行时状态和跨会话记忆应分开建模。"
  },
  S004: {
    title: "MCP 工具上下文",
    strength: "强",
    note: "工具调用把外部动作和外部数据纳入可追踪链路。"
  },
  S005: {
    title: "多模态硬件场景",
    strength: "中",
    note: "设备形态改变输入、输出、隐私和打扰成本。"
  },
  S006: {
    title: "Context Compiler 假设",
    strength: "中",
    note: "从检索到打包的显式编译管线仍需要实验量化。"
  },
  S007: {
    title: "GenUI 结构化输出",
    strength: "中",
    note: "界面计划应由 schema 约束，而不是直接生成不可控 DOM。"
  },
  S008: {
    title: "证据缺口清单",
    strength: "弱",
    note: "开放问题需要进入 backlog，而不是被视觉叙事掩盖。"
  }
};

const intents = [
  {
    id: "learn",
    label: "理解研究",
    title: "快速理解主线",
    description: "按概念依赖生成从 Context Window 到硬件落地的阅读路线。",
    mode: "map",
    evidenceDepth: "normal",
    keywords: ["理解", "学习", "综述", "主线", "解释", "overview"]
  },
  {
    id: "build",
    label: "设计系统",
    title: "生成落地架构",
    description: "突出输入、记忆、编译、设备策略和可实现组件。",
    mode: "assembly",
    evidenceDepth: "medium",
    keywords: ["架构", "系统", "实现", "工程", "产品", "build", "design"]
  },
  {
    id: "verify",
    label: "验证假设",
    title: "暴露证据缺口",
    description: "优先展开证据强度、风险边界和下一步实验任务。",
    mode: "evidence",
    evidenceDepth: "high",
    keywords: ["验证", "证据", "风险", "实验", "缺口", "评估", "verify"]
  },
  {
    id: "demo",
    label: "演示场景",
    title: "生成场景叙事",
    description: "把抽象机制重组为设备、任务和端到端链路。",
    mode: "scenario",
    evidenceDepth: "guided",
    keywords: ["演示", "场景", "用户", "故事", "案例", "demo", "scenario"]
  }
];

const intentRoutes = {
  learn: ["context-window", "sensor-port", "memory-tower", "compiler-factory", "genui-studio", "hardware-lab", "evidence"],
  build: ["sensor-port", "memory-tower", "compiler-factory", "genui-studio", "hardware-lab", "evidence"],
  verify: ["evidence", "context-window", "memory-tower", "compiler-factory", "genui-studio", "hardware-lab"],
  demo: ["hardware-lab", "sensor-port", "compiler-factory", "memory-tower", "genui-studio", "evidence"]
};

const buildingVisuals = {
  "context-window": {
    footprint: { w: 76, d: 50 },
    height: 88,
    rotation: -10,
    color: "teal",
    labelAnchor: "south",
    scaleOnHover: 1.16,
    layer: 3,
    shape: "dome"
  },
  "sensor-port": {
    footprint: { w: 72, d: 46 },
    height: 68,
    rotation: 8,
    color: "blue",
    labelAnchor: "east",
    scaleOnHover: 1.15,
    layer: 4,
    shape: "port"
  },
  "memory-tower": {
    footprint: { w: 64, d: 48 },
    height: 112,
    rotation: -8,
    color: "green",
    labelAnchor: "west",
    scaleOnHover: 1.17,
    layer: 2,
    shape: "tower"
  },
  "compiler-factory": {
    footprint: { w: 86, d: 48 },
    height: 60,
    rotation: 6,
    color: "amber",
    labelAnchor: "south",
    scaleOnHover: 1.14,
    layer: 5,
    shape: "factory"
  },
  "hardware-lab": {
    footprint: { w: 78, d: 52 },
    height: 76,
    rotation: -5,
    color: "violet",
    labelAnchor: "east",
    scaleOnHover: 1.16,
    layer: 5,
    shape: "lab"
  },
  "genui-studio": {
    footprint: { w: 74, d: 52 },
    height: 82,
    rotation: 10,
    color: "teal",
    labelAnchor: "north",
    scaleOnHover: 1.16,
    layer: 6,
    shape: "studio"
  },
  evidence: {
    footprint: { w: 70, d: 50 },
    height: 74,
    rotation: -7,
    color: "red",
    labelAnchor: "south",
    scaleOnHover: 1.14,
    layer: 4,
    shape: "observatory"
  }
};

const world = {
  title: "Context Engineering Living City",
  claim: "这座研究城市会按目标重排路线，并在放大建筑时保持空间连续性。",
  fallback: "如果结构化计划失败，界面会退回到确定性的研究路线。"
};

const buildingBlueprints = [
  {
    id: "context-window",
    kind: "foundation",
    title: "Context Window 观测站",
    subtitle: "一次模型调用能看到什么",
    short: "解释上下文窗口、RAG、记忆、工具上下文和压缩策略的边界。",
    claim: "长上下文不是结构化记忆和上下文选择机制的替代品。",
    componentType: "semantic-map",
    evidenceStrength: "强",
    position: { x: 18, y: 42 },
    color: "teal",
    risk: "容易把 token 上限误当成可靠记忆，从而忽略选择、排序和治理。",
    openQuestion: "不同任务下，窗口位置、摘要粒度和检索结果如何共同影响回答质量？",
    docs: ["S001", "S002"],
    assets: {
      mapTile: asset("world-map-base.png"),
      closeup: asset("sensor-port-base.png"),
      interior: asset("context-window-interior.png")
    },
    rooms: [
      room("window-room", "窗口截面室", "把 system、用户目标、历史、工具结果和输出约束拆成可观察层。", 11, 20, 31, 30, "强", ["S001"], [
        object("prompt-slice", "Prompt 切片台", "拆解一次调用中各段内容的职责。", 28, 42, "schema-panel", "强", ["S001"]),
        object("attention-map", "注意力热区", "标出首尾高权重区域和中段稀释风险。", 70, 58, "heatmap", "强", ["S001"])
      ]),
      room("boundary-room", "边界辨析室", "区分 RAG、Memory、Tool Context 与 Session State。", 45, 18, 34, 32, "中", ["S002", "S004"], [
        object("rag-port", "RAG 接入口", "外部知识按任务相关性进入候选池。", 30, 55, "retrieval", "中", ["S002"]),
        object("tool-ledger", "工具回执台", "把工具调用结果变成可追踪上下文。", 73, 42, "tool-result", "强", ["S004"])
      ]),
      room("compression-room", "压缩实验室", "评估摘要、结构化抽取、选择性遗忘的效果。", 20, 58, 56, 26, "中", ["S001", "S008"], [
        object("summary-press", "摘要压缩机", "把低密度历史压成任务相关摘要。", 34, 42, "compression", "中", ["S001"]),
        object("drop-guard", "遗忘阈值闸", "防止低置信内容长期污染上下文。", 74, 60, "policy", "弱", ["S008"])
      ])
    ]
  },
  {
    id: "sensor-port",
    kind: "sensor",
    title: "多模态传感器港口",
    subtitle: "把现实流变成 Context Object",
    short: "把摄像头、麦克风、IMU、位置和设备状态转成可治理的事件对象。",
    claim: "智能硬件的第一道难题，是把连续世界压缩成可信、可调用的事件对象。",
    componentType: "input-router",
    evidenceStrength: "中",
    position: { x: 39, y: 30 },
    color: "blue",
    risk: "端侧事件切分过粗会丢失任务线索，过细会放大隐私和成本。",
    openQuestion: "端侧设备能否稳定完成隐私过滤和事件边界识别？",
    docs: ["S002", "S005"],
    assets: {
      mapTile: asset("world-map-base.png"),
      closeup: asset("sensor-port-base.png"),
      interior: asset("sensor-port-interior.png")
    },
    rooms: [
      room("capture-room", "采集码头", "对齐视觉、音频、运动和位置输入。", 12, 24, 31, 30, "中", ["S005"], [
        object("camera-rig", "视觉桅杆", "抽取人物、物体、空间关系和文字线索。", 30, 44, "vision", "中", ["S005"]),
        object("audio-bay", "音频泊位", "识别说话人、意图片段和环境声音。", 70, 56, "audio", "中", ["S005"])
      ]),
      room("privacy-room", "隐私闸门", "旁人、位置、敏感场景先过滤再进入记忆。", 48, 18, 29, 33, "中", ["S005", "S008"], [
        object("redaction-gate", "脱敏闸", "在上传和写入记忆前处理敏感字段。", 37, 50, "privacy", "中", ["S005"]),
        object("consent-meter", "同意仪表", "记录可用范围、过期策略和来源。", 76, 36, "governance", "弱", ["S008"])
      ]),
      room("event-room", "事件装配间", "把连续流切分为可写入、可检索、可排序的对象。", 23, 59, 50, 24, "中", ["S002"], [
        object("segmenter", "事件切刀", "按场景变化、活动转换和用户请求切分。", 32, 45, "event", "中", ["S002"]),
        object("object-schema", "对象模具", "为每个 Context Object 附上来源、置信度和优先级。", 70, 54, "schema", "中", ["S002"])
      ])
    ]
  },
  {
    id: "memory-tower",
    kind: "memory",
    title: "七层记忆塔",
    subtitle: "生命周期与治理分层",
    short: "从原始传感器缓冲到治理元信息，展示硬件记忆的层级结构。",
    claim: "智能硬件需要的不是一个长期记忆库，而是按生命周期和用途分层的记忆系统。",
    componentType: "layer-stack",
    evidenceStrength: "强",
    position: { x: 28, y: 68 },
    color: "green",
    risk: "把短期感知、任务状态和长期语义混在一起，会造成延迟、污染和隐私问题。",
    openQuestion: "Episode 到 Semantic 的自动归纳准确率如何验证？",
    docs: ["S003", "S008"],
    assets: {
      mapTile: asset("world-map-base.png"),
      closeup: asset("memory-tower-base.png"),
      interior: asset("memory-tower-interior.png")
    },
    rooms: [
      room("working-room", "工作记忆层", "承载当前任务、当前感知和短期中间结果。", 24, 17, 34, 29, "强", ["S003"], [
        object("task-slate", "任务白板", "保留目标、计划和中间结果。", 34, 42, "state", "强", ["S003"]),
        object("perception-cache", "感知缓存", "保存秒级到分钟级的当前世界状态。", 72, 55, "cache", "中", ["S005"])
      ]),
      room("episode-room", "事件档案层", "把具体时间、地点、人物和任务结果写成 episode。", 16, 52, 31, 28, "强", ["S003"], [
        object("episode-vault", "事件库", "保留可追溯、可过期、可撤销的经历记录。", 36, 46, "archive", "强", ["S003"]),
        object("trace-thread", "追踪线轴", "连接来源、用户确认和后续使用。", 74, 62, "trace", "中", ["S003"])
      ]),
      room("govern-room", "治理中枢", "统一处理来源、权限、置信度、过期和审计。", 53, 34, 30, 36, "中", ["S003", "S008"], [
        object("policy-core", "策略核心", "决定一条记忆能否存、能否用、何时删除。", 42, 45, "policy", "中", ["S003"]),
        object("semantic-distiller", "语义蒸馏器", "从多次 episode 中归纳稳定画像和偏好。", 72, 58, "distill", "弱", ["S008"])
      ])
    ]
  },
  {
    id: "compiler-factory",
    kind: "compiler",
    title: "Context Compiler 工厂",
    subtitle: "调用前的选择、排序与打包",
    short: "在模型调用前决定是否调用、取什么、过滤什么、怎样打包。",
    claim: "智能硬件不能只做 retrieve-then-prompt，需要一个显式 Context Compiler。",
    componentType: "pipeline",
    evidenceStrength: "中",
    position: { x: 57, y: 55 },
    color: "amber",
    risk: "如果先排序再隐私过滤，可能让敏感信息进入不可控候选链路。",
    openQuestion: "Context Ranker 权重应该固定、可学习，还是用户可调？",
    docs: ["S004", "S006"],
    assets: {
      mapTile: asset("world-map-base.png"),
      closeup: asset("compiler-factory-base.png"),
      interior: asset("compiler-factory-interior.png")
    },
    rooms: [
      room("trigger-room", "触发与意图室", "判断是否值得调用模型，以及调用哪类模型。", 11, 31, 27, 28, "中", ["S006"], [
        object("trigger-sensor", "触发探针", "识别用户请求、环境事件和定时任务。", 36, 42, "trigger", "中", ["S006"]),
        object("intent-router", "意图分流器", "选择问答、摘要、行动规划或主动提醒。", 75, 58, "router", "中", ["S006"])
      ]),
      room("rank-room", "检索排序室", "结合任务相关性、空间相关性、置信度、隐私风险和打扰成本。", 40, 17, 36, 33, "中", ["S002", "S006"], [
        object("retrieval-belt", "检索输送带", "从不同记忆层取候选上下文。", 28, 52, "retrieval", "中", ["S002"]),
        object("ranker-table", "多维排序台", "把语义、空间、置信和成本一起评分。", 72, 46, "ranker", "中", ["S006"])
      ]),
      room("packing-room", "Prompt 打包车间", "按注意力模式和 token 预算组装最终输入。", 26, 60, 49, 24, "中", ["S001", "S006"], [
        object("privacy-airlock", "隐私气闸", "过滤敏感、过期和撤销信息。", 28, 42, "privacy", "中", ["S006"]),
        object("packing-arm", "打包机械臂", "将规则、任务、检索结果和约束放到合适位置。", 70, 55, "packing", "中", ["S001"])
      ])
    ]
  },
  {
    id: "hardware-lab",
    kind: "hardware",
    title: "智能硬件实验室",
    subtitle: "设备形态决定上下文策略",
    short: "用眼镜、耳机、AI Pin 和机器人场景验证 Context Pipeline 的实践价值。",
    claim: "不同硬件形态不是换外壳，而是需要不同的上下文权重、记忆重点和输出策略。",
    componentType: "scenario-lab",
    evidenceStrength: "中",
    position: { x: 63, y: 42 },
    color: "violet",
    risk: "主动服务可能打扰用户，机器人场景还会引入物理动作风险。",
    openQuestion: "哪些设备场景链路来自实测，哪些仍只是估算？",
    docs: ["S005", "S008"],
    assets: {
      mapTile: asset("world-map-base.png"),
      closeup: asset("hardware-lab-base.png"),
      interior: asset("hardware-lab-interior.png")
    },
    rooms: [
      room("wearable-room", "可穿戴舱", "眼镜和耳机需要低打扰、高空间相关的输出。", 12, 25, 32, 30, "中", ["S005"], [
        object("glasses-rig", "眼镜台", "把视觉和空间上下文转成轻量 overlay。", 34, 43, "device", "中", ["S005"]),
        object("earbud-pod", "耳机舱", "在音频通道中压缩输出，控制打扰成本。", 73, 58, "device", "中", ["S005"])
      ]),
      room("lifelog-room", "随身记录室", "AI Pin 和个人记录设备强调 episode、治理和隐私。", 48, 20, 30, 32, "中", ["S005", "S008"], [
        object("pin-recorder", "Pin 记录器", "把生活事件写成可撤销的 episodic memory。", 38, 48, "device", "中", ["S005"]),
        object("privacy-shield", "隐私盾", "对旁人、位置和长期录音做前置治理。", 73, 42, "privacy", "弱", ["S008"])
      ]),
      room("robot-room", "机器人场域", "机器人还需要把高层规划和低层动作风险分开。", 24, 61, 52, 23, "中", ["S005"], [
        object("robot-runway", "机器人轨道", "把空间记忆、动作计划和失败学习分层处理。", 34, 48, "robot", "中", ["S005"]),
        object("preflight-check", "行动预检台", "确认有用、可信、低打扰、可解释再执行。", 73, 57, "safety", "中", ["S005"])
      ])
    ]
  },
  {
    id: "genui-studio",
    kind: "genui",
    title: "GenUI 生成工作台",
    subtitle: "结构化 UIPlan 驱动界面",
    short: "按研究意图即时生成解释空间，而不是固定的信息架构。",
    claim: "生成式 UI 的核心不是随机生成视觉，而是把研究对象、证据状态和用户意图编译成可操作界面。",
    componentType: "ui-plan",
    evidenceStrength: "中",
    position: { x: 61, y: 27 },
    color: "teal",
    risk: "直接生成 DOM 会让证据、风险和交互状态失去边界。",
    openQuestion: "界面生成策略能否通过任务完成率和理解效率评估？",
    docs: ["S007", "S008"],
    assets: {
      mapTile: asset("world-map-base.png"),
      closeup: asset("genui-studio-base.png"),
      interior: asset("genui-studio-interior.png")
    },
    rooms: [
      room("intent-room", "意图建模室", "识别用户现在是理解、设计、验证还是演示。", 11, 25, 31, 28, "中", ["S007"], [
        object("intent-console", "意图控制台", "把自然语言目标映射到 UIPlan 参数。", 36, 46, "intent", "中", ["S007"]),
        object("route-solver", "路线求解器", "根据目标生成推荐路径和默认展开节点。", 74, 55, "route", "中", ["S007"])
      ]),
      room("schema-room", "Schema 校验室", "LLM 只输出结构化计划，失败则回退模板。", 46, 20, 32, 33, "中", ["S007", "S008"], [
        object("plan-validator", "计划校验器", "校验意图、镜头、房间、热点和证据层。", 34, 44, "validator", "中", ["S007"]),
        object("fallback-template", "回退模板", "结构不合法时使用确定性视图。", 74, 60, "fallback", "强", ["S007"])
      ]),
      room("composer-room", "组件装配室", "按对象类型生成地图、流程、层级、证据或场景组件。", 23, 60, 52, 24, "中", ["S007"], [
        object("component-router", "组件路由器", "选择卡片、流程、栈、实验或证据工作台。", 32, 48, "component", "中", ["S007"]),
        object("feedback-loop", "反馈回路", "用户点击、搜索和图层选择反向改变生成策略。", 72, 55, "feedback", "弱", ["S008"])
      ])
    ]
  },
  {
    id: "evidence",
    kind: "evidence",
    title: "证据天文台",
    subtitle: "把可信度放回界面中心",
    short: "让关键结论可审查，而不是只靠视觉说服。",
    claim: "高质量展示不能牺牲可信度，每个关键结论都要能回到证据强度和开放问题。",
    componentType: "evidence-board",
    evidenceStrength: "强",
    position: { x: 83, y: 68 },
    color: "red",
    risk: "弱证据如果被包装得太顺滑，会被误用为产品原则。",
    openQuestion: "如何把开放问题转成可复现实验和用户研究？",
    docs: ["S001", "S008"],
    assets: {
      mapTile: asset("world-map-base.png"),
      closeup: asset("evidence-observatory-base.png"),
      interior: asset("evidence-observatory-interior.png")
    },
    rooms: [
      room("source-room", "来源登记室", "维护论文、官方文档、案例和待确认材料的来源链。", 14, 25, 31, 29, "强", ["S001", "S004"], [
        object("source-ledger", "来源账本", "记录每个结论的来源、日期和适用范围。", 33, 45, "source", "强", ["S001"]),
        object("quote-locker", "摘录锁柜", "保留可核查摘录，避免二次转述漂移。", 73, 56, "quote", "强", ["S004"])
      ]),
      room("strength-room", "证据分级室", "把强、中、弱证据分开进入不同设计决策。", 47, 19, 31, 34, "强", ["S001", "S008"], [
        object("strength-scale", "强度秤", "把结论标为架构原则、设计假设或研究 backlog。", 36, 48, "evidence", "强", ["S001"]),
        object("risk-flagger", "风险旗标", "标出尚未实验验证的推导和边界条件。", 73, 41, "risk", "中", ["S008"])
      ]),
      room("question-room", "开放问题室", "把疑问直接转换成下一步实验、访谈或资料补证任务。", 23, 61, 52, 23, "中", ["S008"], [
        object("question-board", "问题墙", "聚合仍缺实测、缺引用或缺定义的问题。", 32, 46, "question", "弱", ["S008"]),
        object("experiment-brief", "实验简报机", "把开放问题改写成可执行验证任务。", 72, 57, "experiment", "中", ["S008"])
      ])
    ]
  }
];

function room(id, title, intro, x, y, w, h, evidenceStrength, docs, objects) {
  return {
    id,
    title,
    intro,
    position: { x, y, w, h },
    scaleLevels: ["building", "room", "object"],
    componentType: "room-map",
    evidenceStrength,
    docs,
    risk: "需要明确适用边界，避免把局部设计推成通用规律。",
    openQuestion: "这里的机制如何通过可复现实验或案例 trace 验证？",
    objects
  };
}

function object(id, title, intro, rx, ry, componentType, evidenceStrength, docs) {
  return {
    id,
    title,
    intro,
    rel: { x: rx, y: ry },
    componentType,
    evidenceStrength,
    docs,
    risk: "该对象如果脱离来源和边界，容易变成过度确定的设计结论。",
    openQuestion: "它在真实硬件场景中的收益、延迟和失败模式如何度量？",
    trace: `UIPlan.hotspots[].id = "${id}"`,
    mechanism: "由结构化研究对象生成热点，再用 HTML/SVG 叠加到 imagegen 底图上。"
  };
}

const buildings = Object.fromEntries(buildingBlueprints.map((building) => {
  const rooms = building.rooms.map((roomItem) => {
    const objects = roomItem.objects.map((objectItem) => ({
      ...objectItem,
      position: {
        x: roomItem.position.x + (roomItem.position.w * objectItem.rel.x) / 100,
        y: roomItem.position.y + (roomItem.position.h * objectItem.rel.y) / 100
      }
    }));
    return { ...roomItem, objects };
  });
  return [building.id, {
    ...building,
    visual: building.visual || buildingVisuals[building.id],
    rooms,
    scaleLevels: {
      world: 0.62,
      building: 1,
      room: 1.36,
      object: 1.72
    }
  }];
}));

const buildingList = Object.values(buildings);

function currentIntent() {
  return intents.find((intent) => intent.id === state.intent) || intents[0];
}

function currentRoute() {
  return intentRoutes[state.intent] || intentRoutes.learn;
}

function inferIntentFromText(text) {
  const query = text.trim().toLowerCase();
  if (!query) return state.intent;
  const scored = intents.map((intent) => {
    const score = intent.keywords.reduce((sum, keyword) => query.includes(keyword.toLowerCase()) ? sum + 1 : sum, 0);
    return { id: intent.id, score };
  }).sort((a, b) => b.score - a.score);
  return scored[0]?.score > 0 ? scored[0].id : state.intent;
}

function generateUIPlan(intentId, focusNode = {}) {
  const intent = intents.find((item) => item.id === intentId) || intents[0];
  const recommendedPath = intentRoutes[intent.id] || intentRoutes.learn;
  const buildingId = focusNode.buildingId || state.camera.buildingId || recommendedPath[0];
  const building = buildings[buildingId] || buildings[recommendedPath[0]];
  const roomId = focusNode.roomId || chooseDefaultRoom(building, intent.id);
  const roomItem = building.rooms.find((item) => item.id === roomId) || building.rooms[0];
  const objectId = focusNode.objectId || roomItem.objects[0]?.id || null;
  const zoomLevel = state.camera.level === "world" ? "world" : state.camera.level;
  const evidenceLayers = {
    evidence: intent.evidenceDepth === "high" || state.layers.evidence,
    risk: intent.id === "verify" || intent.id === "build" || state.layers.risk,
    questions: intent.id === "verify" || state.layers.questions
  };
  const labelDensity = state.selectedBuildingId ? "active" : state.hoveredBuildingId ? "hover" : "minimal";

  const plan = {
    intent: intent.id,
    userGoal: state.userPrompt || intent.description,
    recommendedPath,
    visibleBuildings: buildingList.map((item) => item.id),
    highlightedBuildings: recommendedPath,
    focusBuildingId: building.id,
    labelDensity,
    cameraTarget: {
      level: state.camera.level,
      buildingId,
      roomId,
      objectId
    },
    zoomLevel,
    rooms: building.rooms.map((item) => ({
      id: item.id,
      title: item.title,
      evidenceStrength: item.evidenceStrength,
      visible: intent.id !== "verify" || item.evidenceStrength !== "弱"
    })),
    hotspots: roomItem.objects.map((item) => ({
      id: item.id,
      title: item.title,
      componentType: item.componentType,
      evidenceStrength: item.evidenceStrength
    })),
    detailComponent: detailComponentFor(intent.id, building.kind),
    evidenceLayers,
    fallback: world.fallback
  };

  return validateUIPlan(plan) ? plan : fallbackUIPlan(intent.id, building);
}

function validateUIPlan(plan) {
  return Boolean(
    plan &&
    typeof plan.intent === "string" &&
    Array.isArray(plan.recommendedPath) &&
    plan.recommendedPath.length > 0 &&
    Array.isArray(plan.visibleBuildings) &&
    ["minimal", "hover", "active"].includes(plan.labelDensity) &&
    plan.cameraTarget &&
    ["world", "building", "room", "object"].includes(plan.cameraTarget.level) &&
    Array.isArray(plan.rooms) &&
    Array.isArray(plan.hotspots) &&
    plan.evidenceLayers &&
    typeof plan.fallback === "string"
  );
}

function fallbackUIPlan(intentId, building) {
  const roomItem = building.rooms[0];
  return {
    intent: intentId,
    userGoal: currentIntent().description,
    recommendedPath: intentRoutes.learn,
    visibleBuildings: buildingList.map((item) => item.id),
    highlightedBuildings: intentRoutes.learn,
    focusBuildingId: building.id,
    labelDensity: "minimal",
    cameraTarget: {
      level: "building",
      buildingId: building.id,
      roomId: roomItem.id,
      objectId: roomItem.objects[0]?.id || null
    },
    zoomLevel: "building",
    rooms: building.rooms.map((item) => ({ id: item.id, title: item.title, evidenceStrength: item.evidenceStrength, visible: true })),
    hotspots: roomItem.objects.map((item) => ({ id: item.id, title: item.title, componentType: item.componentType, evidenceStrength: item.evidenceStrength })),
    detailComponent: "deterministic-template",
    evidenceLayers: { evidence: true, risk: false, questions: false },
    fallback: world.fallback
  };
}

function chooseDefaultRoom(building, intentId) {
  if (intentId === "verify") {
    return building.rooms.find((item) => item.evidenceStrength !== "强")?.id || building.rooms[0].id;
  }
  if (intentId === "demo") {
    return building.rooms[building.rooms.length - 1].id;
  }
  if (intentId === "build") {
    return building.rooms.find((item) => item.componentType.includes("room"))?.id || building.rooms[1]?.id || building.rooms[0].id;
  }
  return building.rooms[0].id;
}

function detailComponentFor(intentId, kind) {
  if (intentId === "verify" || kind === "evidence") return "evidence-workbench";
  if (intentId === "build" || kind === "compiler" || kind === "genui") return "assembly-flow";
  if (intentId === "demo" || kind === "hardware") return "scenario-trace";
  return "semantic-map";
}

function visibleLayers() {
  const plan = generateUIPlan(state.intent, state.camera);
  return {
    evidence: state.layers.evidence || plan.evidenceLayers.evidence,
    risk: state.layers.risk || plan.evidenceLayers.risk,
    questions: state.layers.questions || plan.evidenceLayers.questions
  };
}

function render() {
  closeDrawer();
  if (state.camera.level === "world") {
    renderWorld();
  } else {
    renderBuilding();
  }
  applyLayers();
}

function renderWorld() {
  setView("world");
  syncHash();
  const plan = generateUIPlan(state.intent, { level: "world" });
  const route = plan.recommendedPath;

  stage.innerHTML = `
    <section class="world-view semantic-view">
      <div class="world-bg" aria-hidden="true"></div>
      ${renderRouteSvg(route)}
      <article class="world-intro">
        <div class="eyebrow">GenUI city</div>
        <h1>Living City</h1>
      </article>
      <aside class="gen-console" aria-label="生成式研究目标">
        <div class="eyebrow">UIPlan generator</div>
        <h2>${escapeHtml(currentIntent().title)}</h2>
        <p>${escapeHtml(currentIntent().description)}</p>
        <form class="prompt-form" data-intent-form>
          <input name="goal" type="text" value="${escapeAttr(state.userPrompt)}" placeholder="输入研究目标，例如：验证记忆塔的证据缺口" autocomplete="off" />
          <button type="submit">生成</button>
        </form>
        <div class="intent-grid">
          ${intents.map((intent) => `
            <button class="intent-button ${intent.id === state.intent ? "active" : ""}" type="button" data-intent="${intent.id}">
              <strong>${escapeHtml(intent.label)}</strong>
              <span>${escapeHtml(intent.title)}</span>
            </button>
          `).join("")}
        </div>
        <div class="generated-route" aria-label="生成路线">
          ${route.map((id, index) => `<span>${index + 1}. ${escapeHtml(buildings[id].title)}</span>`).join("")}
        </div>
      </aside>
      ${buildingList.map((building) => renderSemanticBuilding(building, route, plan)).join("")}
    </section>
  `;

  bindWorldEvents();
  refreshSearchHighlights();
  applyLayers();
}

function renderRouteSvg(route) {
  const points = route.map((id) => {
    const building = buildings[id];
    return `${building.position.x},${building.position.y}`;
  }).join(" ");

  return `
    <svg class="route-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      <polyline class="route-shadow" points="${points}" />
      <polyline class="route-line" points="${points}" />
      ${route.map((id, index) => {
        const building = buildings[id];
        return `<circle class="route-dot" cx="${building.position.x}" cy="${building.position.y}" r="${index === 0 ? 1.25 : 0.85}" />`;
      }).join("")}
    </svg>
  `;
}

function renderSemanticBuilding(building, route, plan) {
  const order = route.indexOf(building.id);
  const suggested = order !== -1;
  const active = state.selectedBuildingId === building.id || plan.focusBuildingId === building.id && plan.labelDensity === "active";
  const queryText = `${building.title} ${building.subtitle} ${building.short} ${building.claim}`.toLowerCase();
  const searchMatch = state.searchQuery && queryText.includes(state.searchQuery);
  const visual = building.visual;
  return `
    <button
      class="semantic-building shape-${visual.shape} ${suggested ? "is-suggested" : ""} ${active ? "is-active" : ""} ${searchMatch ? "is-focused" : ""} label-${visual.labelAnchor} color-${visual.color}"
      data-building="${building.id}"
      style="${buildingStyle(building)}"
      type="button"
      aria-label="进入${escapeAttr(building.title)}"
    >
      <span class="building-shadow" aria-hidden="true"></span>
      <span class="building-ground" aria-hidden="true"></span>
      <span class="building-volume" aria-hidden="true">
        <i class="building-face front"></i>
        <i class="building-face side"></i>
        <i class="building-face roof"></i>
        <i class="building-core"></i>
      </span>
      ${suggested ? `<b class="route-index">${order + 1}</b>` : ""}
      <span class="building-status" aria-hidden="true">
        <i class="overlay-badge evidence"></i>
        <i class="overlay-badge risk"></i>
        <i class="overlay-badge question"></i>
      </span>
      <span class="building-label">
        <strong>${escapeHtml(shortTitle(building))}</strong>
        <em>${escapeHtml(hoverHint(building))}</em>
      </span>
    </button>
  `;
}

function buildingStyle(building) {
  const visual = building.visual;
  return [
    `--x:${building.position.x}%`,
    `--y:${building.position.y}%`,
    `--footprint-w:${visual.footprint.w}px`,
    `--footprint-d:${visual.footprint.d}px`,
    `--building-h:${visual.height}px`,
    `--rotate:${visual.rotation}deg`,
    `--hover-scale:${visual.scaleOnHover}`,
    `--layer:${visual.layer}`
  ].join(";");
}

function shortTitle(building) {
  const map = {
    "context-window": "Context",
    "sensor-port": "传感器港",
    "memory-tower": "记忆塔",
    "compiler-factory": "Compiler",
    "hardware-lab": "硬件实验室",
    "genui-studio": "GenUI 工作台",
    evidence: "证据天文台"
  };
  return map[building.id] || building.title;
}

function hoverHint(building) {
  const hint = building.subtitle || building.short || building.claim;
  return hint.length > 18 ? `${hint.slice(0, 18)}…` : hint;
}

function renderBuilding() {
  const building = buildings[state.camera.buildingId] || buildings[currentRoute()[0]];
  if (!building) return;

  if (!state.camera.roomId) state.camera.roomId = chooseDefaultRoom(building, state.intent);
  const activeRoom = building.rooms.find((roomItem) => roomItem.id === state.camera.roomId) || building.rooms[0];
  if (!activeRoom) return;
  if (state.camera.level === "object" && !state.camera.objectId) {
    state.camera.objectId = activeRoom.objects[0]?.id || null;
  }

  const activeObject = activeRoom.objects.find((item) => item.id === state.camera.objectId) || null;
  if (activeObject) {
    state.camera.level = "object";
  }
  const plan = generateUIPlan(state.intent, {
    buildingId: building.id,
    roomId: activeRoom.id,
    objectId: activeObject?.id || null
  });

  setView("building");
  syncHash();

  const focusX = activeObject?.position.x || activeRoom.position.x + activeRoom.position.w / 2;
  const focusY = activeObject?.position.y || activeRoom.position.y + activeRoom.position.h / 2;

  stage.innerHTML = `
    <section
      class="building-view semantic-view ${state.motion === "continuity" ? "zoom-enter" : ""} color-${building.color}"
      style="--origin-x:${building.position.x}%; --origin-y:${building.position.y}%; --focus-x:${focusX}%; --focus-y:${focusY}%;"
    >
      <div class="building-bg" style="background-image: url('${building.assets.closeup}')" aria-hidden="true"></div>
      <div class="building-layout">
        <aside class="path-rail">
          <div class="eyebrow">Recommended path</div>
          <h2>${escapeHtml(currentIntent().label)}</h2>
          <div class="path-list">
            ${plan.recommendedPath.map((id, index) => renderPathStep(id, index, building.id)).join("")}
          </div>
          <div class="room-list">
            ${building.rooms.map((roomItem) => renderRoomStep(roomItem, roomItem.id === activeRoom.id)).join("")}
          </div>
        </aside>

        <main class="semantic-main">
          <article class="building-summary">
            <div>
              <div class="eyebrow">Semantic zoom · ${escapeHtml(plan.detailComponent)}</div>
              <h1>${escapeHtml(building.title)}</h1>
              <p>${escapeHtml(building.claim)}</p>
            </div>
            <div class="summary-actions">
              ${renderCameraTabs(building, activeRoom, activeObject)}
              <div class="summary-buttons">
                <button class="action-pill" type="button" data-drawer="ui-plan">UIPlan</button>
                <button class="action-pill" type="button" data-drawer="evidence">证据</button>
                <button class="action-pill" type="button" data-drawer="risk">风险</button>
              </div>
            </div>
          </article>

          <section class="cutaway-stage" data-level="${state.camera.level}" aria-label="${escapeAttr(building.title)}内部空间">
            <div class="cutaway-map" style="background-image:url('${building.assets.interior}')"></div>
            <div class="cutaway-vignette" aria-hidden="true"></div>
            <svg class="room-links" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
              ${renderRoomLinks(building.rooms)}
            </svg>
            <div class="room-layer">
              ${building.rooms.map((roomItem) => renderRoomZone(roomItem, roomItem.id === activeRoom.id)).join("")}
            </div>
            <div class="object-layer">
              ${activeRoom.objects.map((objectItem) => renderObjectHotspot(objectItem, activeObject?.id === objectItem.id)).join("")}
            </div>
            <div class="zoom-readout">
              <strong>${zoomLabel(state.camera.level)}</strong>
              <span>${escapeHtml(activeObject?.title || activeRoom.title)}</span>
            </div>
          </section>
        </main>

        <aside class="detail-panel">
          ${renderDetailPanel(building, activeRoom, activeObject, plan)}
        </aside>
      </div>
    </section>
  `;

  state.motion = "idle";
  bindBuildingEvents();
  refreshSearchHighlights();
  applyLayers();
}

function renderPathStep(id, index, activeId) {
  const item = buildings[id];
  return `
    <button class="path-step ${id === activeId ? "active" : ""}" type="button" data-jump-building="${id}">
      <i>${index + 1}</i>
      <span><strong>${escapeHtml(item.title)}</strong><em>${escapeHtml(item.subtitle)}</em></span>
    </button>
  `;
}

function renderRoomStep(roomItem, active) {
  return `
    <button class="room-step ${active ? "active" : ""}" type="button" data-room="${roomItem.id}">
      <strong>${escapeHtml(roomItem.title)}</strong>
      <span>${escapeHtml(roomItem.intro)}</span>
      <em>${escapeHtml(roomItem.evidenceStrength)}证据 · ${roomItem.objects.length} 热点</em>
    </button>
  `;
}

function renderCameraTabs(building, roomItem, objectItem) {
  const levels = [
    { id: "world", label: "城市" },
    { id: "building", label: "建筑" },
    { id: "room", label: "房间" },
    { id: "object", label: "物件" }
  ];
  return `
    <div class="camera-tabs" aria-label="缩放层级">
      ${levels.map((level) => `
        <button
          type="button"
          data-level="${level.id}"
          aria-pressed="${state.camera.level === level.id}"
          ${level.id === "object" && !objectItem ? "disabled" : ""}
        >${level.label}</button>
      `).join("")}
    </div>
  `;
}

function renderRoomLinks(rooms) {
  const centers = rooms.map((roomItem) => ({
    x: roomItem.position.x + roomItem.position.w / 2,
    y: roomItem.position.y + roomItem.position.h / 2
  }));
  return centers.slice(1).map((point, index) => {
    const prev = centers[index];
    return `<line x1="${prev.x}" y1="${prev.y}" x2="${point.x}" y2="${point.y}" />`;
  }).join("");
}

function renderRoomZone(roomItem, active) {
  const p = roomItem.position;
  return `
    <button
      class="room-zone ${active ? "active" : ""}"
      type="button"
      data-room="${roomItem.id}"
      style="left:${p.x}%; top:${p.y}%; width:${p.w}%; height:${p.h}%;"
    >
      <span class="room-plate">
        <strong>${escapeHtml(roomItem.title)}</strong>
        <em>${escapeHtml(roomItem.evidenceStrength)}证据</em>
      </span>
      <span class="room-hint">${escapeHtml(shortText(roomItem.intro, 18))}</span>
      ${renderLayerBadges()}
    </button>
  `;
}

function renderObjectHotspot(objectItem, active) {
  return `
    <button
      class="object-hotspot ${active ? "active" : ""}"
      type="button"
      data-object="${objectItem.id}"
      style="left:${objectItem.position.x}%; top:${objectItem.position.y}%;"
    >
      <i></i>
      <strong>${escapeHtml(objectItem.title)}</strong>
      <span>${escapeHtml(shortText(objectItem.componentType, 12))}</span>
      ${renderLayerBadges()}
    </button>
  `;
}

function shortText(value, max = 18) {
  const text = String(value || "");
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

function renderDetailPanel(building, roomItem, objectItem, plan) {
  const target = objectItem || roomItem;
  const docs = (target.docs || building.docs).map((id) => evidenceLibrary[id]).filter(Boolean);
  return `
    <div class="detail-head">
      <div class="eyebrow">${escapeHtml(plan.detailComponent)}</div>
      <h2>${escapeHtml(target.title)}</h2>
      <p>${escapeHtml(target.intro || building.short)}</p>
    </div>
    <div class="generated-explain">
      <strong>结构化生成策略</strong>
      <span>${escapeHtml(currentIntent().label)} · ${escapeHtml(plan.zoomLevel)} · ${escapeHtml(target.componentType)}</span>
      <p>${escapeHtml(objectItem?.mechanism || "根据当前意图选择房间、热点、证据层和右侧组件。")}</p>
    </div>
    <div class="trace-card">
      <strong>Trace</strong>
      <code>${escapeHtml(objectItem?.trace || `UIPlan.rooms[].id = "${roomItem.id}"`)}</code>
    </div>
    <div class="evidence-list">
      ${docs.map((doc) => `
        <section>
          <span>${escapeHtml(doc.strength)}证据</span>
          <strong>${escapeHtml(doc.title)}</strong>
          <p>${escapeHtml(doc.note)}</p>
        </section>
      `).join("")}
    </div>
    <div class="risk-question-grid">
      <section>
        <span class="risk-dot dot"></span>
        <strong>风险边界</strong>
        <p>${escapeHtml(target.risk || building.risk)}</p>
      </section>
      <section>
        <span class="question-dot dot"></span>
        <strong>开放问题</strong>
        <p>${escapeHtml(target.openQuestion || building.openQuestion)}</p>
      </section>
    </div>
    <div class="object-list">
      ${roomItem.objects.map((item) => `
        <button class="${objectItem?.id === item.id ? "active" : ""}" type="button" data-object="${item.id}">
          <strong>${escapeHtml(item.title)}</strong>
          <span>${escapeHtml(item.evidenceStrength)}证据</span>
        </button>
      `).join("")}
    </div>
  `;
}

function renderPlanSummary(plan) {
  return `
    <div class="eyebrow">Structured UIPlan</div>
    <h2>${escapeHtml(plan.userGoal)}</h2>
    <dl>
      <div><dt>镜头</dt><dd>${escapeHtml(plan.cameraTarget.level)}</dd></div>
      <div><dt>组件</dt><dd>${escapeHtml(plan.detailComponent)}</dd></div>
      <div><dt>房间</dt><dd>${plan.rooms.length}</dd></div>
      <div><dt>热点</dt><dd>${plan.hotspots.length}</dd></div>
    </dl>
  `;
}

function renderLayerBadges() {
  return `
    <span class="layer-badges" aria-hidden="true">
      <i class="overlay-badge evidence"></i>
      <i class="overlay-badge risk"></i>
      <i class="overlay-badge question"></i>
    </span>
  `;
}

function zoomLabel(level) {
  const labels = {
    world: "城市尺度",
    building: "建筑外观",
    room: "房间展开",
    object: "物件细节"
  };
  return labels[level] || labels.building;
}

function bindWorldEvents() {
  stage.querySelectorAll("[data-building]").forEach((button) => {
    button.addEventListener("pointerenter", () => setHoveredBuilding(button.dataset.building));
    button.addEventListener("pointerleave", () => setHoveredBuilding(null));
    button.addEventListener("focus", () => setHoveredBuilding(button.dataset.building));
    button.addEventListener("blur", () => setHoveredBuilding(null));
    button.addEventListener("pointerdown", () => selectWorldBuilding(button.dataset.building));
    button.addEventListener("click", () => {
      selectWorldBuilding(button.dataset.building);
      enterBuilding(button.dataset.building);
    });
  });
  stage.querySelectorAll("[data-intent]").forEach((button) => {
    button.addEventListener("click", () => {
      state.intent = button.dataset.intent;
      renderWorld();
    });
  });
  const form = stage.querySelector("[data-intent-form]");
  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    state.userPrompt = String(data.get("goal") || "").trim();
    state.intent = inferIntentFromText(state.userPrompt);
    renderWorld();
  });
}

function setHoveredBuilding(id) {
  state.hoveredBuildingId = id;
  state.labelDensity = id ? "hover" : state.selectedBuildingId ? "active" : "minimal";
  app.dataset.hoveredBuilding = id || "";
}

function selectWorldBuilding(id) {
  state.selectedBuildingId = id;
  state.labelDensity = "active";
  stage.querySelectorAll("[data-building]").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.building === id);
  });
}

function bindBuildingEvents() {
  stage.querySelectorAll("[data-room]").forEach((button) => {
    button.addEventListener("click", () => {
      state.camera.level = "room";
      state.camera.roomId = button.dataset.room;
      state.camera.objectId = null;
      renderBuilding();
    });
  });
  stage.querySelectorAll("[data-object]").forEach((button) => {
    button.addEventListener("click", () => {
      state.camera.level = "object";
      state.camera.objectId = button.dataset.object;
      renderBuilding();
    });
  });
  stage.querySelectorAll("[data-level]").forEach((button) => {
    button.addEventListener("click", () => {
      const level = button.dataset.level;
      if (level === "world") {
        enterWorld();
        return;
      }
      if (level === "object" && !state.camera.objectId) {
        const building = buildings[state.camera.buildingId];
        const roomItem = building.rooms.find((item) => item.id === state.camera.roomId) || building.rooms[0];
        state.camera.objectId = roomItem.objects[0]?.id || null;
      }
      state.camera.level = level;
      renderBuilding();
    });
  });
  stage.querySelectorAll("[data-jump-building]").forEach((button) => {
    button.addEventListener("click", () => enterBuilding(button.dataset.jumpBuilding));
  });
  stage.querySelectorAll("[data-drawer]").forEach((button) => {
    button.addEventListener("click", () => openDrawer(button.dataset.drawer));
  });
}

function enterBuilding(id) {
  const building = buildings[id];
  if (!building) return;
  state.camera = {
    level: "building",
    buildingId: id,
    roomId: chooseDefaultRoom(building, state.intent),
    objectId: null
  };
  state.motion = "continuity";
  renderBuilding();
}

function enterWorld() {
  state.camera = {
    level: "world",
    buildingId: null,
    roomId: null,
    objectId: null
  };
  state.hoveredBuildingId = null;
  state.selectedBuildingId = null;
  state.labelDensity = "minimal";
  app.dataset.hoveredBuilding = "";
  renderWorld();
}

function openDrawer(type) {
  const building = buildings[state.camera.buildingId];
  if (!building) return;
  const roomItem = building.rooms.find((item) => item.id === state.camera.roomId) || building.rooms[0];
  const objectItem = roomItem.objects.find((item) => item.id === state.camera.objectId) || null;
  const plan = generateUIPlan(state.intent, state.camera);
  drawer.classList.add("open");
  drawerKicker.textContent = type === "ui-plan" ? "UIPlan" : type === "risk" ? "风险边界" : "证据";

  if (type === "ui-plan") {
    drawerContent.innerHTML = `
      <h2 class="drawer-title">结构化生成计划</h2>
      <div class="drawer-section">
        <h3>当前意图</h3>
        <p>${escapeHtml(currentIntent().title)}：${escapeHtml(plan.userGoal)}</p>
      </div>
      <div class="drawer-section">
        <h3>镜头目标</h3>
        <p>${escapeHtml(plan.cameraTarget.level)} / ${escapeHtml(building.title)} / ${escapeHtml(roomItem.title)}</p>
      </div>
      <div class="drawer-section">
        <h3>推荐路线</h3>
        <ul>${plan.recommendedPath.map((id) => `<li>${escapeHtml(buildings[id].title)}</li>`).join("")}</ul>
      </div>
      <div class="drawer-section">
        <h3>Fallback</h3>
        <p>${escapeHtml(plan.fallback)}</p>
      </div>
    `;
  } else if (type === "risk") {
    drawerContent.innerHTML = `
      <h2 class="drawer-title">${escapeHtml(building.title)}</h2>
      <div class="drawer-section">
        <h3>建筑风险</h3>
        <p>${escapeHtml(building.risk)}</p>
      </div>
      <div class="drawer-section">
        <h3>当前节点风险</h3>
        <p>${escapeHtml((objectItem || roomItem).risk)}</p>
      </div>
      <div class="drawer-section">
        <h3>开放问题</h3>
        <p>${escapeHtml((objectItem || roomItem).openQuestion)}</p>
      </div>
    `;
  } else {
    const docs = [...new Set([...(objectItem?.docs || roomItem.docs), ...building.docs])].map((id) => evidenceLibrary[id]).filter(Boolean);
    drawerContent.innerHTML = `
      <h2 class="drawer-title">证据与来源</h2>
      ${docs.map((doc) => `
        <div class="drawer-section">
          <h3>${escapeHtml(doc.strength)}证据：${escapeHtml(doc.title)}</h3>
          <p>${escapeHtml(doc.note)}</p>
        </div>
      `).join("")}
    `;
  }
}

function closeDrawer() {
  drawer.classList.remove("open");
}

function goBack() {
  if (state.camera.level === "object") {
    state.camera.level = "room";
    state.camera.objectId = null;
    renderBuilding();
  } else if (state.camera.level === "room") {
    state.camera.level = "building";
    renderBuilding();
  } else if (state.camera.level === "building") {
    enterWorld();
  }
}

function setView(view) {
  app.dataset.view = view;
  backButton.disabled = view === "world";
}

function applyLayers() {
  const layers = visibleLayers();
  app.classList.toggle("show-evidence", layers.evidence);
  app.classList.toggle("show-risk", layers.risk);
  app.classList.toggle("show-questions", layers.questions);
  document.querySelectorAll(".layer-toggle").forEach((button) => {
    button.setAttribute("aria-pressed", String(layers[button.dataset.layer]));
  });
}

function refreshSearchHighlights() {
  const query = state.searchQuery;
  stage.querySelectorAll("[data-building]").forEach((node) => {
    const building = buildings[node.dataset.building];
    const haystack = `${building.title} ${building.subtitle} ${building.short} ${building.claim}`.toLowerCase();
    node.classList.toggle("is-focused", Boolean(query && haystack.includes(query)));
  });
  stage.querySelectorAll("[data-room]").forEach((node) => {
    const building = buildings[state.camera.buildingId];
    const roomItem = building?.rooms.find((item) => item.id === node.dataset.room);
    const haystack = roomItem ? `${roomItem.title} ${roomItem.intro}`.toLowerCase() : "";
    node.classList.toggle("is-focused", Boolean(query && haystack.includes(query)));
  });
  stage.querySelectorAll("[data-object]").forEach((node) => {
    const building = buildings[state.camera.buildingId];
    const roomItems = building?.rooms.flatMap((item) => item.objects) || [];
    const objectItem = roomItems.find((item) => item.id === node.dataset.object);
    const haystack = objectItem ? `${objectItem.title} ${objectItem.intro} ${objectItem.componentType}`.toLowerCase() : "";
    node.classList.toggle("is-focused", Boolean(query && haystack.includes(query)));
  });
}

function syncHash() {
  let hash = "";
  if (state.camera.level !== "world" && state.camera.buildingId) {
    hash = `#${state.camera.buildingId}`;
    if (state.camera.roomId) hash += `/${state.camera.roomId}`;
    if (state.camera.objectId) hash += `/${state.camera.objectId}`;
  }
  const target = `${location.pathname}${hash}`;
  if (`${location.pathname}${location.hash}` !== target) {
    history.replaceState(null, "", target);
  }
}

function restoreFromHash() {
  const [buildingId, roomId, objectId] = location.hash.replace("#", "").split("/");
  const building = buildings[buildingId];
  if (!building) {
    enterWorld();
    return;
  }
  const roomItem = building.rooms.find((item) => item.id === roomId) || building.rooms[0];
  const objectItem = roomItem.objects.find((item) => item.id === objectId);
  state.camera = {
    level: objectItem ? "object" : roomId ? "room" : "building",
    buildingId: building.id,
    roomId: roomItem.id,
    objectId: objectItem?.id || null
  };
  state.motion = "idle";
  renderBuilding();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

document.querySelectorAll(".layer-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const layer = button.dataset.layer;
    state.layers[layer] = !state.layers[layer];
    applyLayers();
  });
});

backButton.addEventListener("click", goBack);
drawerClose.addEventListener("click", closeDrawer);

window.addEventListener("hashchange", restoreFromHash);

searchInput.addEventListener("input", () => {
  state.searchQuery = searchInput.value.trim().toLowerCase();
  refreshSearchHighlights();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeDrawer();
});

if (location.hash) {
  restoreFromHash();
} else {
  renderWorld();
}
