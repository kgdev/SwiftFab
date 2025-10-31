# SwiftFab - 3D零件报价系统

完整的制造报价系统，支持 STEP 文件解析、自动报价、Shopify 集成。

## 🏗️ **项目结构**

```
SwiftFab/
├── backend/                    # Python FastAPI 后端
│   ├── main.py                # 主应用程序
│   ├── database.py            # 数据库模型和连接
│   ├── cadquery_step_parser.py # CADQuery STEP文件解析器
│   ├── final_price_calculator.py # 定价计算器
│   ├── shopify_integration.py  # Shopify 集成
│   ├── shopify_oauth.py       # Shopify OAuth
│   ├── config.py              # 配置管理
│   ├── requirements.txt       # Python 依赖
│   └── railway.json          # Railway 部署配置
├── frontend/                  # React + TypeScript 前端
│   ├── src/                  # 源代码
│   ├── public/               # 静态资源
│   ├── package.json          # 前端依赖
│   └── railway.json          # Railway 部署配置
├── scripts/                   # 工具脚本
│   ├── extractor/            # 数据提取脚本
│   │   ├── fabworks_api_client.py    # Fabworks API 客户端
│   │   └── permute_all_materials.py  # 材料排列组合测试
│   └── analyze/              # 数据分析脚本
│       ├── extract_pricing_data.py   # 提取定价数据
│       └── final_pricing_analysis.py # 定价公式分析
├── data/                      # 数据目录（本地）
├── Dockerfile                 # Docker 构建配置
├── railway.json              # Railway 根配置
├── uv.lock                   # UV 依赖锁文件
└── README.md                 # 本文件
```

## 🚀 **本地启动**

### **前置要求**
- Python 3.11+ 
- Node.js 18+
- PostgreSQL（或使用 Railway 数据库）
- UV（Python 包管理器）

### **1. 安装 UV**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### **2. 安装后端依赖**
```bash
cd backend
uv pip install -r requirements.txt
```

### **3. 配置环境变量**

创建 `backend/.env` 文件：
```bash
# 数据库配置（本地 PostgreSQL 或 Railway）
DATABASE_URL=postgresql://user:password@localhost:5432/swiftfab

# Azure Blob Storage（用于文件存储）
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_CONTAINER_NAME=step-files

# Shopify 配置（可选）
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_access_token
SHOPIFY_API_SECRET=your_api_secret
```

### **4. 启动后端**
```bash
cd backend
python main.py
# 或使用 uvicorn
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端将运行在 `http://localhost:8000`

### **5. 启动前端**

在新终端中：
```bash
cd frontend
npm install
npm start
```

前端将运行在 `http://localhost:3000`

### **健康检查**
- 后端健康检查: `http://localhost:8000/api/health`
- 前端: `http://localhost:3000`

## 🚂 **部署到 Railway**

### **方式一：使用 Railway CLI（推荐）**

#### **1. 安装 Railway CLI**
```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (使用 npm)
npm install -g @railway/cli
```

#### **2. 登录 Railway**
```bash
railway login
```

#### **3. 初始化项目**
```bash
# 在项目根目录
railway init
```

#### **4. 链接到现有项目（如果已创建）**
```bash
railway link
```

#### **5. 部署**
```bash
# 部署后端
cd backend
railway up

# 部署前端
cd frontend
railway up
```

### **方式二：通过 GitHub 自动部署**

#### **1. 连接 GitHub 仓库**
- 登录 [Railway Dashboard](https://railway.app/dashboard)
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择 `SwiftFab` 仓库

#### **2. 配置服务**

Railway 会自动检测到 `railway.json` 配置文件。

**后端服务配置：**
```json
{
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "python3 main.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**前端服务配置：**
```json
{
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "npm run serve",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

#### **3. 配置环境变量**

在 Railway Dashboard 中设置：
- `DATABASE_URL` - PostgreSQL 连接字符串（自动提供）
- `AZURE_STORAGE_CONNECTION_STRING` - Azure Blob Storage
- `AZURE_STORAGE_CONTAINER_NAME` - 容器名称
- `SHOPIFY_STORE_URL` - Shopify 店铺 URL
- `SHOPIFY_ACCESS_TOKEN` - Shopify 访问令牌
- `SHOPIFY_API_SECRET` - Shopify API 密钥
- `PORT` - 端口（自动设置）

#### **4. 添加 PostgreSQL 数据库**
- 在 Railway Dashboard 中点击 "New"
- 选择 "Database" → "PostgreSQL"
- Railway 会自动生成 `DATABASE_URL` 环境变量

#### **5. 监控部署**
```bash
# 查看日志
railway logs

# 查看后端日志
railway logs --service backend

# 查看前端日志
railway logs --service frontend
```

### **部署注意事项**

1. **健康检查超时**：设置为 100 秒以适应 CADQuery 初始化
2. **重启策略**：后端设置为最多重试 10 次，前端 5 次
3. **Railpack 构建器**：使用新的 Railpack 替代已弃用的 Nixpacks
4. **端口配置**：使用 `$PORT` 环境变量动态绑定端口

### **验证部署**
- 后端: `https://your-backend-url.railway.app/api/health`
- 前端: `https://your-frontend-url.railway.app/`

## 📊 **数据提取和分析工具**

### **Extractor 脚本 - 数据提取**

位于 `scripts/extractor/` 目录下的脚本用于从 Fabworks API 提取数据。

#### **1. Fabworks API 客户端**

`fabworks_api_client.py` 提供了与 Fabworks tRPC API 交互的客户端。

**基础使用：**
```bash
cd scripts/extractor
python fabworks_api_client.py
```

**主要功能：**
- 获取材料列表
- 获取表面处理选项
- 更新报价信息
- 批量 API 调用

**示例代码：**
```python
from fabworks_api_client import FabworksAPIClient

# 初始化客户端（需要浏览器 Cookie）
client = FabworksAPIClient(cookies="your_cookie_string")

# 获取材料列表
materials = client.get_materials()

# 获取报价详情
quote = client.get_quote("qte_123456789")

# 更新零件材料
client.update_parts_materials(
    quote_id="qte_123456789",
    material_type="Aluminum",
    material_grade="6061-T6",
    thickness=0.125
)
```

#### **2. 材料排列组合测试**

`permute_all_materials.py` 用于测试所有材料组合并保存结果。

**使用方法：**
```bash
cd scripts/extractor

# 基础使用
python permute_all_materials.py --quote-id qte_123456789

# 指定输出前缀
python permute_all_materials.py -q qte_123456789 --output-prefix "test_run"

# 指定材料文件
python permute_all_materials.py -q qte_123456789 --materials-file samples/materials.json
```

**参数说明：**
- `--quote-id, -q`: Fabworks 报价 ID（必需）
- `--output-prefix`: 输出文件前缀（可选）
- `--materials-file`: 材料配置文件路径（默认：`samples/materials.json`）

**功能：**
1. 从 `materials.json` 读取所有材料组合
2. 遍历所有 材料类型 × 材料等级 × 厚度 × 表面处理 的组合
3. 对每个组合调用 Fabworks API 更新报价
4. 保存每个组合的报价结果到 JSON 文件
5. 输出到 `data/` 目录

**输出格式：**
```
data/
├── [output_prefix]_[material]_[grade]_[thickness]_[finish].json
├── ...
```

**示例输出文件名：**
- `test_run_Aluminum_6061-T6_0.125_Anodized-Clear.json`
- `test_run_Steel_Mild_0.25_PowderCoating-Black.json`

### **Analyze 脚本 - 数据分析**

位于 `scripts/analyze/` 目录下的脚本用于分析提取的数据并推导定价公式。

#### **1. 提取定价数据**

`extract_pricing_data.py` 从 JSON 文件中提取定价数据并生成 CSV。

**使用方法：**
```bash
cd scripts/analyze
python extract_pricing_data.py
```

**功能：**
1. 扫描 `data/` 目录下的所有 JSON 文件
2. 提取以下字段：
   - 材料类型（material_type）
   - 材料等级（material_grade）
   - 材料厚度（material_thickness）
   - 表面处理（finish）
   - 零件尺寸（dimensions）
   - 材料使用面积（mat_use_sqin）
   - 切割次数（num_cuts）
   - 单件价格（price_per_part）
3. 生成 `pricing_data.csv` 文件

**输出 CSV 格式：**
```csv
material_type,material_grade,material_thickness,finish,mat_use_sqin,num_cuts,price_per_part
Aluminum,6061-T6,0.125,Anodized-Clear,15.23,45,12.50
Steel,Mild,0.25,PowderCoating-Black,20.15,60,18.75
...
```

#### **2. 定价公式分析**

`final_pricing_analysis.py` 使用机器学习分析定价数据并推导计算公式。

**使用方法：**
```bash
cd scripts/analyze

# 基础分析
python final_pricing_analysis.py

# 指定数据文件
python final_pricing_analysis.py --data-file pricing_data.csv
```

**功能：**
1. **加载数据**：读取 `pricing_data.csv`
2. **特征工程**：
   - 创建组合特征（材料面积 × 厚度）
   - 按材料-等级组合分组
3. **约束线性回归**：
   - 对每个材料组合拟合回归模型
   - 强制所有系数为正数（符合物理意义）
4. **参数提取**：
   - 材料基础成本（material_base_cost）
   - 材料费率（material_rate）：$/（平方英寸 × 英寸）
   - 切割费率（cut_rate）：$/切割次数
   - 表面处理基础成本（finish_base_cost）
   - 表面处理面积费率（finish_surface_rate）：$/平方英寸
5. **可视化分析**：
   - R² 分数热力图
   - 预测 vs 实际价格散点图
   - 残差分析图
6. **输出结果**：
   - `material_parameters.json`: 材料参数
   - `finish_parameters.json`: 表面处理参数
   - `pricing_analysis_report.txt`: 详细分析报告
   - `*.png`: 可视化图表

**定价公式：**

```python
# 材料成本
material_cost = material_base_cost + (mat_use_sqin × thickness × material_rate) + (num_cuts × cut_rate)

# 表面处理成本
finish_cost = finish_base_cost + (mat_use_sqin × finish_surface_rate)

# 总价格
total_price = material_cost + finish_cost
```

**输出示例：**

`material_parameters.json`:
```json
{
  "Aluminum_6061-T6": {
    "base_cost": 5.00,
    "material_rate": 0.15,
    "cut_rate": 0.05,
    "r2_score": 0.98
  },
  "Steel_Mild": {
    "base_cost": 8.00,
    "material_rate": 0.20,
    "cut_rate": 0.08,
    "r2_score": 0.96
  }
}
```

`finish_parameters.json`:
```json
{
  "Anodized-Clear": {
    "base_cost": 10.00,
    "surface_rate": 0.50,
    "r2_score": 0.95
  },
  "PowderCoating-Black": {
    "base_cost": 15.00,
    "surface_rate": 0.75,
    "r2_score": 0.94
  }
}
```

### **完整工作流程**

```bash
# 步骤 1: 提取数据
cd scripts/extractor
python permute_all_materials.py --quote-id qte_YOUR_QUOTE_ID

# 步骤 2: 提取定价数据到 CSV
cd ../analyze
python extract_pricing_data.py

# 步骤 3: 分析定价公式
python final_pricing_analysis.py

# 步骤 4: 查看结果
cat material_parameters.json
cat finish_parameters.json
cat pricing_analysis_report.txt
```

### **数据目录结构**

```
data/
├── *.json                      # Fabworks API 原始数据
├── pricing_data.csv            # 提取的定价数据
├── material_parameters.json    # 材料参数
├── finish_parameters.json      # 表面处理参数
├── pricing_analysis_report.txt # 分析报告
└── *.png                       # 可视化图表
```

## 🎯 **核心功能**

- ✅ **STEP 文件解析**: 基于 CADQuery 的 STEP 文件分析
- ✅ **自动报价生成**: 智能制造报价系统
- ✅ **Shopify 集成**: 完整的电商集成（产品、订单、结账）
- ✅ **Azure Blob 存储**: STEP 文件云存储
- ✅ **PostgreSQL 数据库**: 报价和零件数据管理
- ✅ **响应式 UI**: 现代化 React 界面
- ✅ **健康监控**: 内置健康检查端点
- ✅ **自动重启**: 失败时自动恢复
- ✅ **数据提取工具**: Fabworks API 数据提取
- ✅ **定价分析**: 机器学习定价公式推导

## 🛠️ **技术栈**

### **后端**
- **框架**: FastAPI
- **CAD 解析**: CADQuery 2.4.0
- **数据库**: PostgreSQL + SQLAlchemy
- **存储**: Azure Blob Storage
- **电商**: Shopify API
- **部署**: Railway (Railpack)

### **前端**
- **框架**: React 18 + TypeScript
- **路由**: React Router v6
- **HTTP**: Axios
- **样式**: Tailwind CSS
- **构建**: React Scripts
- **服务**: Serve

### **工具**
- **包管理**: UV (Python), NPM (Node.js)
- **API 客户端**: Fabworks tRPC
- **数据分析**: Pandas, NumPy, Scikit-learn
- **可视化**: Matplotlib, Seaborn

## 📖 **API 文档**

### **健康检查**
```bash
GET /api/health
```
返回后端状态和版本信息。

### **创建报价**
```bash
POST /api/createQuote
Content-Type: multipart/form-data

file: [STEP文件]
```
上传 STEP 文件并生成报价。

### **获取报价**
```bash
GET /api/quotes/{quote_id}
```
获取指定报价的详细信息。

### **结账**
```bash
POST /api/checkout/{quote_id}
```
为报价创建 Shopify 结账链接。

## 🔍 **故障排除**

### **CADQuery 导入错误**
```bash
# 确保 NumPy 版本 < 2.0
uv pip install "numpy<2.0.0"
```

### **数据库连接失败**
- 检查 `DATABASE_URL` 环境变量
- 确保 PostgreSQL 服务运行中
- 检查防火墙规则

### **Azure Blob 存储错误**
- 验证 `AZURE_STORAGE_CONNECTION_STRING`
- 确保容器已创建
- 检查访问权限

### **Shopify API 错误**
- 验证 API 凭证
- 检查 Shopify 店铺状态
- 查看 API 限流日志

## 📝 **开发建议**

1. **本地开发**: 使用 Railway 数据库避免本地 PostgreSQL 配置
2. **环境变量**: 使用 `.env` 文件管理敏感信息
3. **热重载**: 后端使用 `--reload`，前端自动热重载
4. **日志查看**: 使用 `railway logs` 监控生产环境
5. **数据分析**: 定期运行分析脚本更新定价参数

## 🤝 **贡献指南**

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 **许可证**

本项目为私有项目。

## 📧 **联系方式**

如有问题，请联系项目维护者。

---

**最后更新**: 2025-01-24  
**版本**: 2.0.0  
**构建器**: Railpack (Railway)  
**解析器**: CADQuery 2.4.0