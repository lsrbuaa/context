const app = document.getElementById("app");
const stage = document.getElementById("stage");
const backButton = document.getElementById("backButton");
const searchInput = document.getElementById("searchInput");
const drawer = document.getElementById("detailDrawer");
const drawerContent = document.getElementById("drawerContent");
const drawerKicker = document.getElementById("drawerKicker");
const drawerClose = document.getElementById("drawerClose");

const state = {
  view: "world",
  buildingId: null,
  activeItemId: null,
  layers: {
    evidence: false,
    risk: false,
    questions: false
  }
};

const buildings = {
  "context-window": {
    id: "context-window",
    kind: "foundation",
    title: "Context Window 观测站",
    short: "模型一次调用能看到什么，以及为什么不能把它当无限容器。",
    bgClass: "sensor",
    claim: "长上下文不是结构化记忆和上下文选择机制的替代品。",
    why: "Context Window 决定模型一次推理时可访问的信息边界。软件和硬件系统的关键差异，不是 token 上限，而是选择、排序、压缩和治理策略。",
    practice: [
      "先区分 RAG、Memory、Tool Context 和 Session State 的职责，再决定注入方式。",
      "高价值、当前任务相关的信息进入 prompt；低频或大体量信息保留在外部可查询层。",
      "对首尾高注意力区域做结构化布局，避免关键约束落在中间被稀释。"
    ],
    nodes: [
      {
        id: "window-anatomy",
        title: "Context Window 截面",
        caption: "System、用户请求、历史、工具、记忆、输出约束。",
        detail: "它不是一个资料仓库，而是一次推理的工作台。每一块内容都要为当前任务服务。"
      },
      {
        id: "boundary",
        title: "RAG / Memory / Tool 边界",
        caption: "三者解决的问题不同，不能混为一谈。",
        detail: "RAG 取外部知识，Memory 维持跨时段个人化状态，Tool Context 承载外部动作和结果。"
      },
      {
        id: "pitfalls",
        title: "Context 行为现象",
        caption: "Lost in the Middle、Attention Sink、Recency Bias。",
        detail: "这些现象说明 prompt 不是线性容器，位置、噪声和结构都会影响模型行为。"
      },
      {
        id: "compression",
        title: "Compression 策略",
        caption: "摘要、结构化抽取、事件化和选择性遗忘。",
        detail: "压缩的目标不是变短，而是保留对任务有用的高信号信息。"
      }
    ]
  },
  "sensor-port": {
    id: "sensor-port",
    kind: "sensor",
    title: "多模态传感器港口",
    short: "把连续、高噪声、多模态输入转成可用 Context Object。",
    bgClass: "sensor",
    claim: "智能硬件的第一道难题，是把现实世界连续流压缩成可信、可治理、可调用的事件对象。",
    why: "摄像头、麦克风、IMU、位置和设备状态不是 prompt，它们必须先经过对齐、隐私过滤、事件切分和结构化。",
    practice: [
      "隐私过滤应尽量前置到端侧，而不是等到云端推理前再处理。",
      "连续流必须先切成事件，否则记忆系统无法写入和召回。",
      "Context Object 要显式携带置信度、来源、隐私级别和 prompt 优先级。"
    ],
    nodes: [
      {
        id: "camera",
        title: "Camera",
        caption: "人物、物体、空间关系、文字。",
        detail: "视觉输入带宽最高，适合先转成 scene.people、scene.objects 和 spatial_context。"
      },
      {
        id: "microphone",
        title: "Microphone",
        caption: "转录、说话人、环境声、情绪。",
        detail: "音频既是任务线索，也是隐私风险源。耳机和 Pin 场景中权重尤其高。"
      },
      {
        id: "imu-location",
        title: "IMU + Location",
        caption: "动作、姿态、地点、移动状态。",
        detail: "这些低带宽信号很适合做触发器和空间相关性判断。"
      },
      {
        id: "privacy",
        title: "Privacy Gate",
        caption: "旁人、位置、敏感场景先过滤。",
        detail: "旁人数据、敏感地点和长时录音必须在进入长期记忆前被治理。"
      },
      {
        id: "event",
        title: "Event Segmentation",
        caption: "连续流变成可写入事件。",
        detail: "事件边界可以来自场景变化、活动转换、人物出入、日历或用户请求。"
      },
      {
        id: "context-object",
        title: "Context Object",
        caption: "统一字段承载场景、状态、记忆链接和优先级。",
        detail: "这是传感器世界和 Compiler 世界之间的标准接口。"
      }
    ]
  },
  "memory-tower": {
    id: "memory-tower",
    kind: "memory",
    title: "七层记忆塔",
    short: "从原始传感器缓存到治理元信息的智能硬件记忆结构。",
    bgClass: "memory",
    claim: "智能硬件需要的不是一个长期记忆库，而是按生命周期、用途和治理要求分层的记忆系统。",
    why: "感知状态每秒变化，任务状态按分钟变化，情景和语义记忆跨天月演化。混在一起会导致延迟、污染和隐私问题。",
    practice: [
      "把 Perception Working Memory 和 Task Working Memory 分开，避免传感器刷新不断重构任务上下文。",
      "Episodic Memory 用来记录事件，Semantic Memory 才承载稳定画像和偏好。",
      "Governance Memory 不是附加功能，而是覆盖所有记忆层的元信息。"
    ],
    nodes: [
      { id: "l7", level: "L7", title: "Governance Memory", caption: "来源、权限、置信度、过期、审计。", life: "全周期", detail: "治理层决定一条记忆能否存、能否用、能否上云、何时删除。" },
      { id: "l6", level: "L6", title: "Procedural Memory", caption: "行为规则、服务策略、习惯模式。", life: "长期", detail: "例如会议中只震动提醒，不语音打断。" },
      { id: "l5", level: "L5", title: "Semantic Memory", caption: "用户画像、稳定事实、人物关系。", life: "月到年", detail: "从多次 episode 中归纳出的稳定知识。" },
      { id: "l4", level: "L4", title: "Episodic Memory", caption: "具体事件，带时间地点人物。", life: "天到月", detail: "例如昨天会议里用户承诺本周提交材料。" },
      { id: "l3", level: "L3", title: "Task Working Memory", caption: "当前任务目标、计划、中间结果。", life: "任务级", detail: "最接近 prompt 的动态工作台。" },
      { id: "l2", level: "L2", title: "Perception Working Memory", caption: "当前看到、听到、感知到什么。", life: "秒到分钟", detail: "实时更新，但不应该全量进入 prompt。" },
      { id: "l1", level: "L1", title: "Raw Sensor Buffer", caption: "原始音视频和传感器环形缓存。", life: "秒级", detail: "短期缓存，只在需要追溯或确认时使用。" }
    ]
  },
  "compiler-factory": {
    id: "compiler-factory",
    kind: "compiler",
    title: "Context Compiler 工厂",
    short: "模型调用前，决定是否调用、取什么、过滤什么、怎样打包。",
    bgClass: "compiler",
    claim: "智能硬件不能只做 retrieve-then-prompt，需要一个显式的 Context Compiler。",
    why: "硬件场景同时受任务相关性、空间相关性、隐私风险、打扰成本、token 预算和输出通道约束。",
    practice: [
      "Privacy Filter 必须排在 Ranking 和 Packing 之前。",
      "Ranking 不应只看语义相似度，还要看空间、置信度、可行动性和打扰成本。",
      "Prompt Packing 要利用首尾高注意力区域，把当前任务和安全约束放到更可靠的位置。"
    ],
    nodes: [
      { id: "trigger", title: "Trigger Detection", caption: "是否需要调用模型。", detail: "用户请求、环境事件、定时任务和程序性规则都可能触发模型调用。" },
      { id: "intent", title: "Intent Classification", caption: "确定 LLM / VLM / VLA 和输出通道。", detail: "问答、摘要、动作规划和主动提醒需要不同 context 结构。" },
      { id: "retrieval", title: "Context Retrieval", caption: "从七层记忆取候选。", detail: "L2/L3 可全量注入，L4/L5 Top-K，L6 条件匹配，L7 用于过滤。" },
      { id: "privacy-filter", title: "Privacy Filter", caption: "先过滤再排序。", detail: "敏感数据、旁人数据、过期记忆和撤销记忆不能进入后续流程。" },
      { id: "ranking", title: "Context Ranking", caption: "多维评分，而非纯语义检索。", detail: "TaskRelevance、Recency、SpatialRelevance、Confidence、PrivacyRisk、InterruptionCost 都影响排序。" },
      { id: "budget", title: "Token Budget", caption: "把预算分给必要区块。", detail: "超预算时先压缩背景记忆，再降低低置信内容，最后删除弱相关信息。" },
      { id: "packing", title: "Prompt Packing", caption: "按注意力模式布局。", detail: "头部放稳定规则，尾部放当前任务和安全约束，中间放背景和检索结果。" },
      { id: "invoke", title: "Model Invocation", caption: "调用 LLM / VLM / VLA。", detail: "不同模型类型决定输入结构和输出约束。" },
      { id: "feedback", title: "Feedback Update", caption: "执行反馈写回记忆。", detail: "成功强化，失败反思，用户否决则降权或删除。" }
    ]
  },
  "hardware-lab": {
    id: "hardware-lab",
    kind: "hardware",
    title: "智能硬件实验室",
    short: "用设备场景验证 Context Pipeline 的实践价值。",
    bgClass: "hardware",
    claim: "不同硬件形态不是换一套外壳，而是需要不同的 context 权重、记忆重点和输出策略。",
    why: "眼镜有视觉和 overlay，耳机输出极短，AI Pin 长时记录隐私风险高，机器人还要处理物理动作风险。",
    practice: [
      "先按设备输出通道反推 context budget 和主动服务策略。",
      "AI 眼镜重视空间和人物 context；耳机重视音频和打扰成本；机器人重视程序性和空间记忆。",
      "所有主动服务都要先做 pre-flight check：有用、可信、低打扰、可解释。"
    ],
    nodes: [
      { id: "glasses", title: "AI 眼镜", caption: "会议准备、人物识别、安全提醒。", detail: "视觉和空间 context 强，适合低打扰视觉 overlay。" },
      { id: "earbuds", title: "AI 耳机", caption: "会议辅助、人名提醒、语言辅助。", detail: "输出极短，InterruptionCost 权重最高。" },
      { id: "pin", title: "AI Pin", caption: "会议摘要、承诺追踪、生活日志。", detail: "Episodic 和 Governance Memory 是核心，隐私风险最高。" },
      { id: "robot", title: "机器人", caption: "物品整理、失败学习、主动陪伴。", detail: "需要 high-level planning context 和 low-level action context 分离。" }
    ]
  },
  "evidence": {
    id: "evidence",
    kind: "evidence",
    title: "证据天文台",
    short: "让关键结论可被审查，而不是只靠视觉说服。",
    bgClass: "evidence",
    claim: "高质量展示不能牺牲可信度，每个关键结论都要能回到证据强度和开放问题。",
    why: "这套研究既有强证据，也有设计推导和待验证假设。展示时需要让听众知道哪些能直接用，哪些还要验证。",
    practice: [
      "强证据结论可作为架构原则。",
      "中弱证据结论应作为设计假设，并进入验证计划。",
      "开放问题要直接转成下一步调研任务，而不是隐藏在文档末尾。"
    ],
    nodes: [
      { id: "strong", title: "强证据", caption: "论文实验或官方文档明确支持。", detail: "例如 Lost in the Middle、MCP 定位、LangGraph state/memory 区分。" },
      { id: "medium", title: "中证据", caption: "可信来源或架构推导支持。", detail: "例如 Compiler 的 9 步 pipeline 和设备差异策略。" },
      { id: "weak", title: "弱证据", caption: "类比推理或尚待产品验证。", detail: "例如某些阈值、遗忘半衰期和主动服务权重。" },
      { id: "questions", title: "开放问题", caption: "下一步调研和验证任务。", detail: "例如 interruption cost 如何量化、ranker 权重是否可学习。" }
    ]
  }
};

const worldNodes = [
  { id: "context-window", x: 9, y: 34, title: "Context Window", subtitle: "一次调用能看到什么", chip: "基础" },
  { id: "sensor-port", x: 26, y: 58, title: "Sensor Port", subtitle: "连续流变成 Context Object", chip: "输入" },
  { id: "memory-tower", x: 47, y: 28, title: "七层记忆塔", subtitle: "按生命周期组织记忆", chip: "架构" },
  { id: "compiler-factory", x: 61, y: 55, title: "Compiler 工厂", subtitle: "选择、过滤、排序、打包", chip: "核心" },
  { id: "hardware-lab", x: 78, y: 34, title: "Hardware Lab", subtitle: "用设备场景验证", chip: "实践" },
  { id: "evidence", x: 76, y: 67, title: "证据天文台", subtitle: "结论可信度和缺口", chip: "证据" }
];

const scenarioSteps = [
  ["场景", "用户走进会议室，AI 眼镜识别会议开始前 3 分钟。"],
  ["输入", "摄像头、日历、位置和设备状态生成 Context Object。"],
  ["记忆", "召回上次会议承诺、参会人关系和提醒偏好。"],
  ["编译", "Compiler 过滤隐私数据，排序高相关记忆，打包 prompt。"],
  ["输出", "以视觉 overlay 提醒用户：上次承诺的材料还未确认。"],
  ["反馈", "用户确认后强化该提醒策略，否决则降权。"]
];

function iconPathForKind(kind) {
  const map = {
    foundation: "M4 19V5l8-3 8 3v14l-8 3-8-3zM12 2v20",
    sensor: "M12 3v18M3 12h18M5 5l14 14M19 5L5 19",
    memory: "M5 5h14v14H5zM8 8h8M8 12h8M8 16h5",
    compiler: "M4 7h16M4 12h16M4 17h16M8 4v16M16 4v16",
    hardware: "M6 8h12v8H6zM9 16v3M15 16v3M9 5v3M15 5v3",
    evidence: "M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.4 6.7 19.1l1-5.8L1.9 9.2l5.9-.9z"
  };
  return map[kind] || map.foundation;
}

function setView(view) {
  state.view = view;
  app.dataset.view = view;
}

function renderWorld() {
  setView("world");
  state.buildingId = null;
  state.activeItemId = null;
  closeDrawer();
  stage.innerHTML = `
    <section class="world-view">
      <div class="world-bg"></div>
      <div class="fallback-city" aria-hidden="true">
        <div class="district-block"></div><div class="district-block"></div><div class="district-block"></div>
        <div class="district-block"></div><div class="district-block"></div><div class="district-block"></div><div class="district-block"></div>
      </div>
      <div class="main-route" aria-hidden="true"></div>
      <article class="hero-card">
        <div class="eyebrow">Research conclusion map</div>
        <h1>下一代 AI 终端的关键能力是 Context Assembly</h1>
        <p>这不是资料库界面，而是一张面向理解和实践的研究地图：从软件 context 管理出发，解释智能硬件如何把现实世界输入编译成模型可用上下文。</p>
      </article>
      <aside class="map-legend">
        <h2>演示路径</h2>
        <ol>
          <li>理解 Context Window 的边界</li>
          <li>把多模态输入转成 Context Object</li>
          <li>用七层记忆管理生命周期和治理</li>
          <li>通过 Compiler 决定该给模型看什么</li>
          <li>用硬件场景验证实践策略</li>
        </ol>
      </aside>
      ${worldNodes.map(renderWorldNode).join("")}
    </section>
  `;
  bindWorldEvents();
  applyLayers();
}

function renderWorldNode(node) {
  return `
    <button class="world-node" data-building="${node.id}" style="left:${node.x}%; top:${node.y}%;" type="button">
      <strong>${node.title}</strong>
      <span>${node.subtitle}</span>
      <div class="node-meta">
        <em class="node-chip">${node.chip}</em>
        <em class="node-chip">进入</em>
      </div>
      <i class="overlay-badge evidence" style="right:12px; top:10px;"></i>
      <i class="overlay-badge risk" style="right:30px; top:10px;"></i>
      <i class="overlay-badge question" style="right:48px; top:10px;"></i>
    </button>
  `;
}

function bindWorldEvents() {
  stage.querySelectorAll("[data-building]").forEach((button) => {
    button.addEventListener("click", () => renderBuilding(button.dataset.building));
  });
}

function renderBuilding(id) {
  const building = buildings[id];
  if (!building) return;
  setView("building");
  state.buildingId = id;
  state.activeItemId = building.nodes[0]?.id || null;
  closeDrawer();

  stage.innerHTML = `
    <section class="building-view">
      <div class="building-bg ${building.bgClass}"></div>
      <div class="building-layout">
        <aside class="side-rail">
          <h2>深挖路径</h2>
          <p>${building.short}</p>
          <div class="node-list">
            ${building.nodes.map((item) => renderSideNode(item, item.id === state.activeItemId)).join("")}
          </div>
        </aside>
        <section class="building-main">
          <article class="building-summary">
            <div>
              <div class="eyebrow">${building.kind} interior</div>
              <h1>${building.title}</h1>
              <p>${building.claim}</p>
            </div>
            <div class="summary-actions">
              <button class="action-pill" type="button" data-drawer="why">为什么重要</button>
              <button class="action-pill" type="button" data-drawer="practice">实践指导</button>
              <button class="action-pill" type="button" data-drawer="evidence">查看证据</button>
            </div>
          </article>
          <div class="visual-system">
            ${renderVisual(building)}
            <i class="overlay-badge evidence" style="left:24px; top:24px;"></i>
            <i class="overlay-badge risk" style="right:26px; top:28px;"></i>
            <i class="overlay-badge question" style="left:50%; bottom:24px;"></i>
          </div>
        </section>
        <aside class="practice-panel">
          <h2>默认结论</h2>
          <div class="claim">${building.claim}</div>
          <h3>实践指导</h3>
          <ul>${building.practice.map((item) => `<li>${item}</li>`).join("")}</ul>
          <div id="activeDetail" class="step-detail"></div>
        </aside>
      </div>
    </section>
  `;
  bindBuildingEvents();
  updateActiveDetail();
  applyLayers();
}

function renderSideNode(item, active) {
  return `
    <button class="side-node ${active ? "active" : ""}" type="button" data-item="${item.id}">
      <strong>${item.level ? `${item.level} · ` : ""}${item.title}</strong>
      <span>${item.caption}</span>
    </button>
  `;
}

function renderVisual(building) {
  if (building.kind === "memory") return renderMemoryTower(building);
  if (building.kind === "sensor") return renderSensorPort(building);
  if (building.kind === "hardware") return renderHardwareLab(building);
  if (building.kind === "evidence") return renderEvidence(building);
  if (building.kind === "compiler") return renderCompiler(building);
  return renderConceptGrid(building);
}

function renderCompiler(building) {
  return `
    <div class="flow-line" aria-hidden="true"></div>
    <div class="flow-canvas">
      <div class="flow-grid">
        ${building.nodes.map((item, index) => `
          <button class="machine ${item.id === state.activeItemId ? "active" : ""}" type="button" data-item="${item.id}">
            <span class="machine-index">${String(index + 1).padStart(2, "0")}</span>
            <strong>${item.title}</strong>
            <span>${item.caption}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

function renderSensorPort(building) {
  return `
    <div class="flow-line" aria-hidden="true"></div>
    <div class="flow-canvas">
      <div class="sensor-grid">
        ${building.nodes.map((item) => `
          <button class="sensor-card ${item.id === state.activeItemId ? "active" : ""}" type="button" data-item="${item.id}">
            <strong>${item.title}</strong>
            <span>${item.caption}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

function renderMemoryTower(building) {
  return `
    <div class="tower-canvas">
      <div class="tower-stack">
        ${building.nodes.map((item) => `
          <button class="memory-floor ${item.id === state.activeItemId ? "active" : ""}" type="button" data-item="${item.id}">
            <span class="floor-level">${item.level}</span>
            <span><strong>${item.title}</strong><span>${item.caption}</span></span>
            <span class="floor-life">${item.life}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

function renderHardwareLab(building) {
  return `
    <div class="lab-canvas">
      <div class="lab-grid">
        ${building.nodes.map((item) => `
          <button class="lab-device ${item.id === state.activeItemId ? "active" : ""}" type="button" data-item="${item.id}">
            <strong>${item.title}</strong>
            <span>${item.caption}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

function renderEvidence(building) {
  return `
    <div class="evidence-canvas">
      <div class="evidence-grid">
        ${building.nodes.map((item) => `
          <button class="evidence-star ${item.id === state.activeItemId ? "active" : ""}" type="button" data-item="${item.id}">
            <strong>${item.title}</strong>
            <span>${item.caption}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

function renderConceptGrid(building) {
  return `
    <div class="flow-canvas">
      <div class="sensor-grid">
        ${building.nodes.map((item) => `
          <button class="sensor-card ${item.id === state.activeItemId ? "active" : ""}" type="button" data-item="${item.id}">
            <strong>${item.title}</strong>
            <span>${item.caption}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;
}

function bindBuildingEvents() {
  stage.querySelectorAll("[data-item]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeItemId = button.dataset.item;
      refreshBuildingSelection();
      updateActiveDetail();
    });
  });
  stage.querySelectorAll("[data-drawer]").forEach((button) => {
    button.addEventListener("click", () => openDrawer(button.dataset.drawer));
  });
}

function refreshBuildingSelection() {
  stage.querySelectorAll("[data-item]").forEach((el) => {
    el.classList.toggle("active", el.dataset.item === state.activeItemId);
  });
}

function updateActiveDetail() {
  const building = buildings[state.buildingId];
  if (!building) return;
  const item = building.nodes.find((node) => node.id === state.activeItemId) || building.nodes[0];
  const detail = document.getElementById("activeDetail");
  if (!detail || !item) return;

  const scenario = building.kind === "hardware" && item.id === "glasses"
    ? `<h2>AI 眼镜会议场景</h2><div class="scenario-timeline">${scenarioSteps.map((step, index) => `
        <div class="timeline-step ${index < 4 ? "active" : ""}">
          <i>${index + 1}</i>
          <span><strong>${step[0]}</strong><span>${step[1]}</span></span>
        </div>
      `).join("")}</div>`
    : "";

  detail.innerHTML = `
    <h2>${item.level ? `${item.level} · ` : ""}${item.title}</h2>
    <p>${item.detail}</p>
    ${scenario}
  `;
}

function openDrawer(type) {
  const building = buildings[state.buildingId];
  if (!building) return;
  drawer.classList.add("open");
  drawerKicker.textContent = type === "evidence" ? "证据层" : type === "practice" ? "实践层" : "解释层";
  if (type === "why") {
    drawerContent.innerHTML = `
      <h2 class="drawer-title">${building.title}</h2>
      <div class="drawer-section">
        <h3>为什么重要</h3>
        <p>${building.why}</p>
      </div>
      <div class="drawer-section">
        <h3>默认主结论</h3>
        <p>${building.claim}</p>
      </div>
    `;
  } else if (type === "practice") {
    drawerContent.innerHTML = `
      <h2 class="drawer-title">实践指导</h2>
      <div class="drawer-section">
        <h3>可以直接用于设计决策</h3>
        <ul>${building.practice.map((item) => `<li>${item}</li>`).join("")}</ul>
      </div>
    `;
  } else {
    drawerContent.innerHTML = `
      <h2 class="drawer-title">证据与验证</h2>
      <div class="drawer-section">
        <h3>证据强度</h3>
        <p>本界面默认只显示结论，证据层用于判断哪些结论可直接作为架构原则，哪些仍是设计假设。</p>
      </div>
      <div class="drawer-section">
        <h3>建议处理</h3>
        <ul>
          <li>强证据：进入架构原则和产品规范。</li>
          <li>中证据：进入方案设计，但保留验证指标。</li>
          <li>弱证据：进入研究 backlog，不直接固化到产品。</li>
        </ul>
      </div>
    `;
  }
}

function closeDrawer() {
  drawer.classList.remove("open");
}

function applyLayers() {
  app.classList.toggle("show-evidence", state.layers.evidence);
  app.classList.toggle("show-risk", state.layers.risk);
  app.classList.toggle("show-questions", state.layers.questions);
  document.querySelectorAll(".layer-toggle").forEach((button) => {
    button.setAttribute("aria-pressed", String(state.layers[button.dataset.layer]));
  });
}

document.querySelectorAll(".layer-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const layer = button.dataset.layer;
    state.layers[layer] = !state.layers[layer];
    applyLayers();
  });
});

backButton.addEventListener("click", renderWorld);
drawerClose.addEventListener("click", closeDrawer);

searchInput.addEventListener("input", () => {
  const query = searchInput.value.trim().toLowerCase();
  if (state.view !== "world") renderWorld();
  stage.querySelectorAll(".world-node").forEach((node) => {
    const building = buildings[node.dataset.building];
    const haystack = `${building.title} ${building.short} ${building.claim}`.toLowerCase();
    node.classList.toggle("is-focused", query.length > 0 && haystack.includes(query));
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeDrawer();
});

renderWorld();
