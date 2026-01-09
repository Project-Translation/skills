# Node/TypeScript MCP 服务器实现指南

## 概述

本文档提供了使用 MCP TypeScript SDK 实现 MCP 服务器的 Node/TypeScript 特定最佳实践和示例。涵盖项目结构、服务器设置、工具注册模式、Zod 输入验证、错误处理和完整的可用示例。

---

## 快速参考

### 关键导入
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import express from "express";
import { z } from "zod";
```

### 服务器初始化
```typescript
const server = new McpServer({
  name: "service-mcp-server",
  version: "1.0.0"
});
```

### 工具注册模式
```typescript
server.registerTool(
  "tool_name",
  {
    title: "Tool Display Name",
    description: "What the tool does",
    inputSchema: { param: z.string() },
    outputSchema: { result: z.string() }
  },
  async ({ param }) => {
    const output = { result: `Processed: ${param}` };
    return {
      content: [{ type: "text", text: JSON.stringify(output) }],
      structuredContent: output // Modern pattern for structured data
    };
  }
);
```

---

## MCP TypeScript SDK

官方 MCP TypeScript SDK 提供：
- `McpServer` 类用于服务器初始化
- `registerTool` 方法用于工具注册
- Zod schema 集成用于运行时输入验证
- 类型安全的工具处理器实现

**重要 - 仅使用现代 API：**
- **使用**：`server.registerTool()`, `server.registerResource()`, `server.registerPrompt()`
- **不使用**：旧的已弃用 API，如 `server.tool()`, `server.setRequestHandler(ListToolsRequestSchema, ...)` 或手动处理器注册
- `register*` 方法提供更好的类型安全、自动 schema 处理，是推荐方法

详见参考资料中的 MCP SDK 文档。

## 服务器命名约定

Node/TypeScript MCP 服务器必须遵循以下命名模式：
- **格式**：`{service}-mcp-server`（小写，带连字符）
- **示例**：`github-mcp-server`, `jira-mcp-server`, `stripe-mcp-server`

名称应：
- 通用（不与特定功能绑定）
- 描述要集成的服务/API
- 易于从任务描述中推断
- 不带版本号或日期

## 项目结构

为 Node/TypeScript MCP 服务器创建以下结构：

```
{service}-mcp-server/
├── package.json
├── tsconfig.json
├── README.md
├── src/
│   ├── index.ts          # 主入口点，包含 McpServer 初始化
│   ├── types.ts          # TypeScript 类型定义和接口
│   ├── tools/            # 工具实现（每个域一个文件）
│   ├── services/         # API 客户端和共享实用工具
│   ├── schemas/          # Zod 验证 schema
│   └── constants.ts      # 共享常量（API_URL、CHARACTER_LIMIT 等）
└── dist/                 # 构建的 JavaScript 文件（入口点：dist/index.js）
```

## 工具实现

### 工具命名

工具名称使用 snake_case（如 "search_users", "create_project", "get_channel_info"），使用清晰、以动词为导向的名称。

**避免命名冲突**：包含服务上下文以防止重叠：
- 使用 "slack_send_message" 而不是 "send_message"
- 使用 "github_create_issue" 而不是 "create_issue"
- 使用 "asana_list_tasks" 而不是 "list_tasks"

### 工具结构

工具使用 `registerTool` 方法注册，需满足以下要求：
- 使用 Zod schema 进行运行时输入验证和类型安全
- `description` 字段必须显式提供 - JSDoc 注释不会自动提取
- 显式提供 `title`, `description`, `inputSchema`, 和 `annotations`
- `inputSchema` 必须是 Zod schema 对象（不是 JSON schema）
- 显式键入所有参数和返回值

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "example-mcp",
  version: "1.0.0"
});

// Zod schema 用于输入验证
const UserSearchInputSchema = z.object({
  query: z.string()
    .min(2, "Query must be at least 2 characters")
    .max(200, "Query must not exceed 200 characters")
    .describe("Search string to match against names/emails"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip for pagination"),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
}).strict();

// 来自 Zod schema 的类型定义
type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

server.registerTool(
  "example_search_users",
  {
    title: "Search Example Users",
    description: `Search for users in the Example system by name, email, or team.

This tool searches across all user profiles in the Example platform, supporting partial matches and various search filters. It does NOT create or modify users, only searches existing ones.

Args:
  - query (string): Search string to match against names/emails
  - limit (number): Maximum results to return, between 1-100 (default: 20)
  - offset (number): Number of results to skip for pagination (default: 0)
  - response_format ('markdown' | 'json'): Output format (default: 'markdown')

Returns:
  For JSON format: Structured data with schema:
  {
    "total": number,           // Total number of matches found
    "count": number,           // Number of results in this response
    "offset": number,          // Current pagination offset
    "users": [
      {
        "id": string,          // User ID (e.g., "U123456789")
        "name": string,        // Full name (e.g., "John Doe")
        "email": string,       // Email address
        "team": string,        // Team name (optional)
        "active": boolean      // Whether user is active
      }
    ],
    "has_more": boolean,       // Whether more results are available
    "next_offset": number      // Offset for next page (if has_more is true)
  }

Examples:
  - Use when: "Find all marketing team members" -> params with query="team:marketing"
  - Use when: "Search for John's account" -> params with query="john"
  - Don't use when: You need to create a user (use example_create_user instead)

Error Handling:
  - Returns "Error: Rate limit exceeded" if too many requests (429 status)
  - Returns "No users found matching '<query>'" if search returns empty`,
    inputSchema: UserSearchInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params: UserSearchInput) => {
    try {
      // 输入验证由 Zod schema 处理
      // 使用验证后的参数进行 API 请求
      const data = await makeApiRequest<any>(
        "users/search",
        "GET",
        undefined,
        {
          q: params.query,
          limit: params.limit,
          offset: params.offset
        }
      );

      const users = data.users || [];
      const total = data.total || 0;

      if (!users.length) {
        return {
          content: [{
            type: "text",
            text: `No users found matching '${params.query}'`
          }]
        };
      }

      // 准备结构化输出
      const output = {
        total,
        count: users.length,
        offset: params.offset,
        users: users.map((user: any) => ({
          id: user.id,
          name: user.name,
          email: user.email,
          ...(user.team ? { team: user.team } : {}),
          active: user.active ?? true
        })),
        has_more: total > params.offset + users.length,
        ...(total > params.offset + users.length ? {
          next_offset: params.offset + users.length
        } : {})
      };

      // 根据请求的格式格式化文本表示
      let textContent: string;
      if (params.response_format === ResponseFormat.MARKDOWN) {
        const lines = [`# User Search Results: '${params.query}'`, "",
          `Found ${total} users (showing ${users.length})`, ""];
        for (const user of users) {
          lines.push(`## ${user.name} (${user.id})`);
          lines.push(`- **Email**: ${user.email}`);
          if (user.team) lines.push(`- **Team**: ${user.team}`);
          lines.push("");
        }
        textContent = lines.join("\n");
      } else {
        textContent = JSON.stringify(output, null, 2);
      }

      return {
        content: [{ type: "text", text: textContent }],
        structuredContent: output // Modern pattern for structured data
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: handleApiError(error)
        }]
      };
    }
  }
);
```

## Zod Schema 输入验证

Zod 提供运行时类型验证：

```typescript
import { z } from "zod";

// 带验证的基本 schema
const CreateUserSchema = z.object({
  name: z.string()
    .min(1, "Name is required")
    .max(100, "Name must not exceed 100 characters"),
  email: z.string()
    .email("Invalid email format"),
  age: z.number()
    .int("Age must be a whole number")
    .min(0, "Age cannot be negative")
    .max(150, "Age cannot be greater than 150")
}).strict();  // 使用 .strict() 禁止额外字段

// 枚举
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

const SearchSchema = z.object({
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format")
});

// 带默认值的可选字段
const PaginationSchema = z.object({
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip")
});
```

## 响应格式选项

支持多种输出格式以提高灵活性：

```typescript
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

const inputSchema = z.object({
  query: z.string(),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
});
```

**Markdown 格式**：
- 使用标题、列表和格式以提高清晰度
- 将时间戳转换为人类可读格式
- 显示带 ID 的显示名称
- 省略冗长的元数据
- 合理分组相关信息

**JSON 格式**：
- 返回完整、结构化的数据，适合程序化处理
- 包含所有可用字段和元数据
- 使用一致的字段名和类型

## 分页实现

用于列出资源的工具：

```typescript
const ListSchema = z.object({
  limit: z.number().int().min(1).max(100).default(20),
  offset: z.number().int().min(0).default(0)
});

async function listItems(params: z.infer<typeof ListSchema>) {
  const data = await apiRequest(params.limit, params.offset);

  const response = {
    total: data.total,
    count: data.items.length,
    offset: params.offset,
    items: data.items,
    has_more: data.total > params.offset + data.items.length,
    next_offset: data.total > params.offset + data.items.length
      ? params.offset + data.items.length
      : undefined
  };

  return JSON.stringify(response, null, 2);
}
```

## 字符限制和截断

添加 CHARACTER_LIMIT 常量以防止响应过大：

```typescript
// constants.ts 中的模块级
export const CHARACTER_LIMIT = 25000;  // 最大响应大小（字符）

async function searchTool(params: SearchInput) {
  let result = generateResponse(data);

  // 检查字符限制并在需要时截断
  if (result.length > CHARACTER_LIMIT) {
    const truncatedData = data.slice(0, Math.max(1, data.length / 2));
    response.data = truncatedData;
    response.truncated = true;
    response.truncation_message =
      `Response truncated from ${data.length} to ${truncatedData.length} items. ` +
      `Use 'offset' parameter or add filters to see more results.`;
    result = JSON.stringify(response, null, 2);
  }

  return result;
}
```

## 错误处理

提供清晰、可操作的错误消息：

```typescript
import axios, { AxiosError } from "axios";

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response) {
      switch (error.response.status) {
        case 404:
          return "Error: Resource not found. Please check the ID is correct.";
        case 403:
          return "Error: Permission denied. You don't have access to this resource.";
        case 429:
          return "Error: Rate limit exceeded. Please wait before making more requests.";
        default:
          return `Error: API request failed with status ${error.response.status}`;
      }
    } else if (error.code === "ECONNABORTED") {
      return "Error: Request timed out. Please try again.";
    }
  }
  return `Error: Unexpected error occurred: ${error instanceof Error ? error.message : String(error)}`;
}
```

## 共享实用工具

提取常见功能到可重用函数：

```typescript
// 共享 API 请求函数
async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  data?: any,
  params?: any
): Promise<T> {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}/${endpoint}`,
      data,
      params,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
}
```

## 异步/等待最佳实践

始终对网络请求和 I/O 操作使用 async/await：

```typescript
// 好：异步网络请求
async function fetchData(resourceId: string): Promise<ResourceData> {
  const response = await axios.get(`${API_URL}/resource/${resourceId}`);
  return response.data;
}

// 坏：Promise 链
function fetchData(resourceId: string): Promise<ResourceData> {
  return axios.get(`${API_URL}/resource/${resourceId}`)
    .then(response => response.data);  // 更难阅读和维护
}
```

## TypeScript 最佳实践

1. **使用严格的 TypeScript**：在 tsconfig.json 中启用严格模式
2. **定义接口**：为所有数据结构创建清晰的接口定义
3. **避免 `any`**：使用正确的类型或 `unknown` 而不是 `any`
4. **Zod 用于运行时验证**：使用 Zod schema 验证外部数据
5. **类型守卫**：为复杂类型检查创建类型守卫函数
6. **错误处理**：始终使用带正确错误类型检查的 try-catch
7. **空值安全**：使用可选链 (`?.`) 和空值合并 (`??`)

```typescript
// 好：使用 Zod 和接口的类型安全
interface UserResponse {
  id: string;
  name: string;
  email: string;
  team?: string;
  active: boolean;
}

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  team: z.string().optional(),
  active: z.boolean()
});

type User = z.infer<typeof UserSchema>;

async function getUser(id: string): Promise<User> {
  const data = await apiCall(`/users/${id}`);
  return UserSchema.parse(data);  // 运行时验证
}

// 坏：使用 any
async function getUser(id: string): Promise<any> {
  return await apiCall(`/users/${id}`);  // 无类型安全
}
```

## 包配置

### package.json

```json
{
  "name": "{service}-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for {Service} API integration",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "clean": "rm -rf dist"
  },
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.6.1",
    "axios": "^1.7.9",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "tsx": "^4.19.2",
    "typescript": "^5.7.2"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## 完整示例

```typescript
#!/usr/bin/env node
/**
 * MCP Server for Example Service.
 *
 * This server provides tools to interact with Example API, including user search,
 * project management, and data export capabilities.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import axios, { AxiosError } from "axios";

// 常量
const API_BASE_URL = "https://api.example.com/v1";
const CHARACTER_LIMIT = 25000;

// 枚举
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

// Zod schema
const UserSearchInputSchema = z.object({
  query: z.string()
    .min(2, "Query must be at least 2 characters")
    .max(200, "Query must not exceed 200 characters")
    .describe("Search string to match against names/emails"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip for pagination"),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
}).strict();

type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

// 共享实用工具函数
async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  data?: any,
  params?: any
): Promise<T> {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}/${endpoint}`,
      data,
      params,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
}

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response) {
      switch (error.response.status) {
        case 404:
          return "Error: Resource not found. Please check the ID is correct.";
        case 403:
          return "Error: Permission denied. You don't have access to this resource.";
        case 429:
          return "Error: Rate limit exceeded. Please wait before making more requests.";
        default:
          return `Error: API request failed with status ${error.response.status}`;
      }
    } else if (error.code === "ECONNABORTED") {
      return "Error: Request timed out. Please try again.";
    }
  }
  return `Error: Unexpected error occurred: ${error instanceof Error ? error.message : String(error)}`;
}

// 创建 MCP 服务器实例
const server = new McpServer({
  name: "example-mcp",
  version: "1.0.0"
});

// 注册工具
server.registerTool(
  "example_search_users",
  {
    title: "Search Example Users",
    description: `[Full description as shown above]`,
    inputSchema: UserSearchInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params: UserSearchInput) => {
    // 如上所示的实现
  }
);

// 主函数
// 用于 stdio（本地）：
async function runStdio() {
  if (!process.env.EXAMPLE_API_KEY) {
    console.error("ERROR: EXAMPLE_API_KEY environment variable is required");
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server running via stdio");
}

// 用于流式 HTTP（远程）：
async function runHTTP() {
  if (!process.env.EXAMPLE_API_KEY) {
    console.error("ERROR: EXAMPLE_API_KEY environment variable is required");
    process.exit(1);
  }

  const app = express();
  app.use(express.json());

  app.post('/mcp', async (req, res) => {
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true
    });
    res.on('close', () => transport.close());
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  });

  const port = parseInt(process.env.PORT || '3000');
  app.listen(port, () => {
    console.error(`MCP server running on http://localhost:${port}/mcp`);
  });
}

// 根据环境选择传输
const transport = process.env.TRANSPORT || 'stdio';
if (transport === 'http') {
  runHTTP().catch(error => {
    console.error("Server error:", error);
    process.exit(1);
  });
} else {
  runStdio().catch(error => {
    console.error("Server error:", error);
    process.exit(1);
  });
}
```

---

## 高级 MCP 功能

### 资源注册

通过基于 URI 的访问暴露数据作为资源：

```typescript
import { ResourceTemplate } from "@modelcontextprotocol/sdk/types.js";

// 注册带 URI 模板的资源
server.registerResource(
  {
    uri: "file://documents/{name}",
    name: "Document Resource",
    description: "Access documents by name",
    mimeType: "text/plain"
  },
  async (uri: string) => {
    // 从 URI 中提取参数
    const match = uri.match(/^file:\/\/documents\/(.+)$/);
    if (!match) {
      throw new Error("Invalid URI format");
    }

    const documentName = match[1];
    const content = await loadDocument(documentName);

    return {
      contents: [{
        uri,
        mimeType: "text/plain",
        text: content
      }]
    };
  }
);

// 动态列出可用资源
server.registerResourceList(async () => {
  const documents = await getAvailableDocuments();
  return {
    resources: documents.map(doc => ({
      uri: `file://documents/${doc.name}`,
      name: doc.name,
      mimeType: "text/plain",
      description: doc.description
    }))
  };
});
```

**何时使用资源 vs 工具：**
- **资源**：用于具有简单基于 URI 参数的数据访问
- **工具**：用于需要验证和业务逻辑的复杂操作
- **资源**：当数据相对静态或基于模板时
- **工具**：当操作有副作用或复杂工作流时

### 传输选项

TypeScript SDK 支持两种主要传输机制：

#### 流式 HTTP（推荐用于远程服务器）

```typescript
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";

const app = express();
app.use(express.json());

app.post('/mcp', async (req, res) => {
  // 为每个请求创建新的传输（无状态，防止请求 ID 冲突）
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true
  });

  res.on('close', () => transport.close());

  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

app.listen(3000);
```

#### stdio（用于本地集成）

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const transport = new StdioServerTransport();
await server.connect(transport);
```

**传输选择：**
- **流式 HTTP**：Web 服务、远程访问、多个客户端
- **stdio**：命令行工具、本地开发、子进程集成

### 通知支持

当服务器状态更改时通知客户端：

```typescript
// 通知工具列表更改
server.notification({
  method: "notifications/tools/list_changed"
});

// 通知资源更改
server.notification({
  method: "notifications/resources/list_changed"
});
```

谨慎使用通知 - 仅当服务器功能真正更改时才使用。

---

## 代码最佳实践

### 代码组合性和可重用性

您的实现必须优先考虑组合性和代码重用：

1. **提取常见功能**：
   - 为跨多个工具使用的操作创建可重用的辅助函数
   - 为 HTTP 请求构建共享的 API 客户端，而不是复制代码
   - 在辅助函数中集中错误处理逻辑
   - 将业务逻辑提取到可以组合的专用函数中
   - 提取共享的 markdown 或 JSON 字段选择和格式化功能

2. **避免重复**：
   - 切勿在工具之间复制类似的代码
   - 如果发现自己写了两次类似的逻辑，将其提取到函数中
   - 分页、过滤、字段选择和格式化等常见操作应共享
   - 认证/授权逻辑应集中

## 构建和运行

构建前始终构建 TypeScript 代码：

```bash
# 构建项目
npm run build

# 运行服务器
npm start

# 开发时自动重载
npm run dev
```

在认为实现完成之前，始终确保 `npm run build` 成功完成。

## 质量检查清单

在最终确定 Node/TypeScript MCP 服务器实现之前，确保：

### 战略设计
- [ ] 工具启用完整工作流，而不仅仅是 API 端点包装器
- [ ] 工具名称反映自然任务细分
- [ ] 响应格式针对代理上下文效率进行优化
- [ ] 在适当的地方使用人类可读标识符
- [ ] 错误消息指导代理正确使用

### 实现质量
- [ ] 专注实现：实现最重要和最有价值的工具
- [ ] 所有工具使用 `registerTool` 注册并完成配置
- [ ] 所有工具包含 `title`, `description`, `inputSchema`, 和 `annotations`
- [ ] 正确设置注释（readOnlyHint, destructiveHint, idempotentHint, openWorldHint）
- [ ] 所有工具使用 Zod schema 进行运行时输入验证，使用 `.strict()` 强制执行
- [ ] 所有 Zod schema 有适当的约束和描述性错误消息
- [ ] 所有工具有全面的描述，包含显式输入/输出类型
- [ ] 描述包含返回值示例和完整 schema 文档
- [ ] 错误消息清晰、可操作且具有教育意义

### TypeScript 质量
- [ ] 为所有数据结构定义 TypeScript 接口
- [ ] 在 tsconfig.json 中启用严格 TypeScript
- [ ] 不使用 `any` 类型 - 使用 `unknown` 或正确类型
- [ ] 所有异步函数有显式 Promise<T> 返回类型
- [ ] 错误处理使用适当的类型守卫（如 `axios.isAxiosError`, `z.ZodError`）

### 高级功能（适用时）
- [ ] 为适当的数据端点注册资源
- [ ] 配置适当的传输（stdio 或流式 HTTP）
- [ ] 为动态服务器功能实现通知
- [ ] 使用 SDK 接口的类型安全

### 项目配置
- [ ] Package.json 包含所有必要的依赖项
- [ ] 构建脚本在 dist/ 目录中生成工作的 JavaScript
- [ ] 主入口点正确配置为 dist/index.js
- [ ] 服务器名称遵循格式：`{service}-mcp-server`
- [ ] tsconfig.json 正确配置严格模式

### 代码质量
- [ ] 在适用的地方正确实现分页
- [ ] 大响应检查 CHARACTER_LIMIT 常量并在需要时截断并显示清晰消息
- [ ] 为潜在大量结果集提供过滤选项
- [ ] 所有网络操作优雅地处理超时和连接错误
- [ ] 提取常见功能到可重用函数
- [ ] 类似操作的返回类型一致

### 测试和构建
- [ ] `npm run build` 成功完成，无错误
- [ ] 创建并可执行 dist/index.js
- [ ] 服务器运行：`node dist/index.js --help`
- [ ] 所有导入正确解析
- [ ] 示例工具调用按预期工作