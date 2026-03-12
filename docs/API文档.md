# 抖音评论情感分析系统 - API文档

## 1. API概述

### 1.1 基本信息
- **Base URL**: `http://localhost:3001/api`
- **Python服务URL**: `http://localhost:5000`
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 认证方式
系统使用JWT（JSON Web Token）进行认证，需要在请求头中携带token：

```
Authorization: Bearer <token>
```

### 1.3 响应格式
所有API响应统一格式：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

错误响应格式：

```json
{
  "success": false,
  "message": "错误信息"
}
```

### 1.4 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 2. 认证模块（Auth）

### 2.1 用户注册

**接口地址**: `POST /api/auth/register`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名（3-20字符） |
| password | String | 是 | 密码（6-20字符） |
| email | String | 是 | 邮箱地址 |

**请求示例**:

```json
{
  "username": "testuser",
  "password": "123456",
  "email": "test@example.com"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2.2 用户登录

**接口地址**: `POST /api/auth/login`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码 |

**请求示例**:

```json
{
  "username": "testuser",
  "password": "123456"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2.3 获取用户信息

**接口地址**: `GET /api/auth/user/:id`

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 用户ID |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "created_at": "2024-01-01T00:00:00.000Z"
  }
}
```

### 2.4 修改密码

**接口地址**: `POST /api/auth/change-password`

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| oldPassword | String | 是 | 旧密码 |
| newPassword | String | 是 | 新密码（6-20字符） |

**请求示例**:

```json
{
  "oldPassword": "123456",
  "newPassword": "654321"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "密码修改成功"
}
```

## 3. 用户管理模块（User）

### 3.1 获取用户列表

**接口地址**: `GET /api/users`

**请求头**:

```
Authorization: Bearer <token>
```

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 页码，默认1 |
| pageSize | Integer | 否 | 每页数量，默认10 |
| keyword | String | 否 | 搜索关键词 |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "created_at": "2024-01-01T00:00:00.000Z"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 10
  }
}
```

### 3.2 创建用户

**接口地址**: `POST /api/users`

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码 |
| email | String | 是 | 邮箱 |
| role | String | 否 | 角色，默认'user' |

**请求示例**:

```json
{
  "username": "newuser",
  "password": "123456",
  "email": "newuser@example.com",
  "role": "user"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "用户创建成功",
  "data": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com",
    "role": "user"
  }
}
```

### 3.3 批量创建用户

**接口地址**: `POST /api/users/batch`

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| users | Array | 是 | 用户数组 |

**请求示例**:

```json
{
  "users": [
    {
      "username": "user1",
      "password": "123456",
      "email": "user1@example.com"
    },
    {
      "username": "user2",
      "password": "123456",
      "email": "user2@example.com"
    }
  ]
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "批量创建成功",
  "data": {
    "successCount": 2,
    "failedCount": 0
  }
}
```

### 3.4 更新用户

**接口地址**: `PUT /api/users/:id`

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 用户ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 否 | 用户名 |
| email | String | 否 | 邮箱 |
| role | String | 否 | 角色 |

**请求示例**:

```json
{
  "username": "updateduser",
  "email": "updated@example.com",
  "role": "admin"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "用户更新成功",
  "data": {
    "id": 1,
    "username": "updateduser",
    "email": "updated@example.com",
    "role": "admin"
  }
}
```

### 3.5 删除用户

**接口地址**: `DELETE /api/users/:id`

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 用户ID |

**响应示例**:

```json
{
  "success": true,
  "message": "用户删除成功"
}
```

## 4. 视频管理模块（Video）

### 4.1 获取视频列表

**接口地址**: `GET /api/videos`

**请求头**:

```
Authorization: Bearer <token>
```

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 页码，默认1 |
| pageSize | Integer | 否 | 每页数量，默认10 |
| keyword | String | 否 | 搜索关键词 |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "videos": [
      {
        "id": 1,
        "video_id": "7123456789012345678",
        "title": "视频标题",
        "author": "作者名称",
        "url": "https://www.douyin.com/video/7123456789012345678",
        "comment_count": 100,
        "created_by": 1,
        "created_at": "2024-01-01T00:00:00.000Z"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 10
  }
}
```

### 4.2 获取视频详情

**接口地址**: `GET /api/videos/:id`

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 视频ID |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "video_id": "7123456789012345678",
    "title": "视频标题",
    "author": "作者名称",
    "url": "https://www.douyin.com/video/7123456789012345678",
    "comment_count": 100,
    "created_by": 1,
    "created_at": "2024-01-01T00:00:00.000Z"
  }
}
```

### 4.3 创建视频

**接口地址**: `POST /api/videos`

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| video_id | String | 是 | 抖音视频ID |
| title | String | 是 | 视频标题 |
| author | String | 是 | 作者名称 |
| url | String | 是 | 视频链接 |
| comment_count | Integer | 否 | 评论数，默认0 |

**请求示例**:

```json
{
  "video_id": "7123456789012345678",
  "title": "视频标题",
  "author": "作者名称",
  "url": "https://www.douyin.com/video/7123456789012345678",
  "comment_count": 100
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "视频创建成功",
  "data": {
    "id": 1,
    "video_id": "7123456789012345678",
    "title": "视频标题",
    "author": "作者名称",
    "url": "https://www.douyin.com/video/7123456789012345678",
    "comment_count": 100,
    "created_by": 1
  }
}
```

### 4.4 删除视频

**接口地址**: `DELETE /api/videos/:id`

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 视频ID |

**响应示例**:

```json
{
  "success": true,
  "message": "视频删除成功"
}
```

### 4.5 下载CSV文件

**接口地址**: `GET /api/videos/:id/download-csv`

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Integer | 是 | 视频ID |

**响应**: CSV文件流

## 5. 评论爬取模块（Crawl）

### 5.1 爬取评论

**接口地址**: `POST /api/crawl/crawl-comments`

**请求头**:

```
Authorization: Bearer <token>
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| url | String | 是 | 抖音视频链接 |
| maxComments | Integer | 否 | 最大评论数，默认100 |

**请求示例**:

```json
{
  "url": "https://www.douyin.com/video/7123456789012345678",
  "maxComments": 100
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "评论爬取成功",
  "data": {
    "video_id": "7123456789012345678",
    "title": "视频标题",
    "comment_count": 100,
    "csv_path": "data/视频标题.csv"
  }
}
```

## 6. 评论数据模块（Comments）

### 6.1 获取评论数据

**接口地址**: `GET /api/comments`

**请求头**:

```
Authorization: Bearer <token>
x-user-id: <user_id>
```

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| video_id | String | 是 | 视频ID |
| sentiment | String | 否 | 情感类型（positive/negative/neutral/all） |
| title | String | 是 | 视频标题（用于定位CSV文件） |

**请求示例**:

```
GET /api/comments?video_id=7123456789012345678&sentiment=positive&title=视频标题
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "id": 1,
        "user_name": "用户名",
        "content": "评论内容",
        "sentiment": "positive",
        "created_at": "2024-01-01 12:00:00"
      }
    ],
    "total": 1
  }
}
```

## 7. 数据分析模块（Python服务）

### 7.1 情感分析

**接口地址**: `POST http://localhost:5000/api/sentiment-analysis`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| videoId | String | 是 | 视频ID |
| title | String | 是 | 视频标题 |
| model | String | 否 | 模型类型，默认'random_forest' |

**请求示例**:

```json
{
  "videoId": "7123456789012345678",
  "title": "视频标题",
  "model": "random_forest"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "total": 100,
    "positive": 60,
    "negative": 20,
    "neutral": 20,
    "positive_ratio": 60.0,
    "negative_ratio": 20.0,
    "neutral_ratio": 20.0,
    "chart": "base64_encoded_image"
  }
}
```

### 7.2 情感趋势分析

**接口地址**: `POST http://localhost:5000/api/sentiment-trend`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| videoId | String | 是 | 视频ID |
| title | String | 是 | 视频标题 |
| model | String | 否 | 模型类型，默认'random_forest' |
| timeDimension | String | 否 | 时间维度（daily/monthly），默认'daily' |

**请求示例**:

```json
{
  "videoId": "7123456789012345678",
  "title": "视频标题",
  "model": "random_forest",
  "timeDimension": "daily"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "daily": [
      {
        "date": "2024-01-01",
        "positive": 10,
        "negative": 3,
        "neutral": 2
      }
    ],
    "monthly": [
      {
        "date": "2024-01",
        "positive": 100,
        "negative": 30,
        "neutral": 20
      }
    ],
    "total_comments": 150,
    "positive_count": 90,
    "negative_count": 30,
    "neutral_count": 30,
    "positive_ratio": 60.0,
    "negative_ratio": 20.0,
    "neutral_ratio": 20.0,
    "chart": "base64_encoded_image"
  }
}
```

### 7.3 词云分析

**接口地址**: `POST http://localhost:5000/api/wordcloud`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| videoId | String | 是 | 视频ID |
| title | String | 是 | 视频标题 |
| minCount | Integer | 否 | 最小出现次数，默认3 |

**请求示例**:

```json
{
  "videoId": "7123456789012345678",
  "title": "视频标题",
  "minCount": 3
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "keywords": [
      {
        "word": "关键词",
        "count": 10
      }
    ],
    "chart": "base64_encoded_image"
  }
}
```

### 7.4 地区分布分析

**接口地址**: `POST http://localhost:5000/api/region-distribution`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| videoId | String | 是 | 视频ID |
| title | String | 是 | 视频标题 |
| minCount | Integer | 否 | 最小评论数，默认3 |

**请求示例**:

```json
{
  "videoId": "7123456789012345678",
  "title": "视频标题",
  "minCount": 3
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "regions": [
      {
        "region": "北京",
        "count": 50
      }
    ],
    "total": 100,
    "chart": "base64_encoded_image"
  }
}
```

### 7.5 数量趋势分析

**接口地址**: `POST http://localhost:5000/api/quantity-trend`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| videoId | String | 是 | 视频ID |
| title | String | 是 | 视频标题 |
| timeDimension | String | 否 | 时间维度（daily/monthly），默认'daily' |

**请求示例**:

```json
{
  "videoId": "7123456789012345678",
  "title": "视频标题",
  "timeDimension": "daily"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "type": "daily",
    "data": [
      {
        "date": "2024-01-01",
        "count": 15
      }
    ],
    "total": 100,
    "chart": "base64_encoded_image"
  }
}
```

### 7.6 生成报告

**接口地址**: `POST http://localhost:5000/api/generate-report`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| videoId | String | 是 | 视频ID |
| title | String | 是 | 视频标题 |
| config | Object | 是 | 报告配置 |

**config参数说明**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| quantityTrend | Boolean | 否 | 是否包含数量趋势 |
| trendTimeDimension | String | 否 | 数量趋势时间维度（daily/monthly） |
| sentimentAnalysis | Boolean | 否 | 是否包含情感分析 |
| sentimentModel | String | 否 | 情感分析模型 |
| sentimentTrend | Boolean | 否 | 是否包含情感趋势 |
| sentimentTrendTimeDimension | String | 否 | 情感趋势时间维度（daily/monthly） |
| sentimentTrendModel | String | 否 | 情感趋势分析模型 |
| wordCloud | Boolean | 否 | 是否包含词云 |
| minKeywordCount | Integer | 否 | 最小关键词出现次数 |
| regionDistribution | Boolean | 否 | 是否包含地区分布 |
| minRegionCount | Integer | 否 | 最小地区评论数 |

**请求示例**:

```json
{
  "videoId": "7123456789012345678",
  "title": "视频标题",
  "config": {
    "quantityTrend": true,
    "trendTimeDimension": "daily",
    "sentimentAnalysis": true,
    "sentimentModel": "random_forest",
    "sentimentTrend": true,
    "sentimentTrendTimeDimension": "daily",
    "sentimentTrendModel": "random_forest",
    "wordCloud": true,
    "minKeywordCount": 3,
    "regionDistribution": true,
    "minRegionCount": 3
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "report": "<html>...</html>",
  "message": "报告生成成功"
}
```

## 8. 错误码说明

### 8.1 通用错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数错误 |
| 1002 | 数据不存在 |
| 1003 | 数据已存在 |
| 1004 | 操作失败 |

### 8.2 认证错误码

| 错误码 | 说明 |
|--------|------|
| 2001 | 用户名或密码错误 |
| 2002 | Token无效 |
| 2003 | Token已过期 |
| 2004 | 无权限访问 |

### 8.3 数据分析错误码

| 错误码 | 说明 |
|--------|------|
| 3001 | CSV文件不存在 |
| 3002 | CSV文件格式错误 |
| 3003 | 数据量不足 |
| 3004 | 模型训练失败 |
| 3005 | 图表生成失败 |

## 9. 使用示例

### 9.1 完整流程示例

#### 9.1.1 用户注册并登录

```javascript
// 1. 注册
const registerResponse = await fetch('http://localhost:3001/api/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'testuser',
    password: '123456',
    email: 'test@example.com'
  })
});

const registerData = await registerResponse.json();
console.log(registerData);

// 2. 登录
const loginResponse = await fetch('http://localhost:3001/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'testuser',
    password: '123456'
  })
});

const loginData = await loginResponse.json();
const token = loginData.data.token;
```

#### 9.1.2 爬取评论并分析

```javascript
// 1. 爬取评论
const crawlResponse = await fetch('http://localhost:3001/api/crawl/crawl-comments', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    url: 'https://www.douyin.com/video/7123456789012345678',
    maxComments: 100
  })
});

const crawlData = await crawlResponse.json();

// 2. 情感分析
const sentimentResponse = await fetch('http://localhost:5000/api/sentiment-analysis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    videoId: crawlData.data.video_id,
    title: crawlData.data.title,
    model: 'random_forest'
  })
});

const sentimentData = await sentimentResponse.json();
console.log(sentimentData);
```

#### 9.1.3 生成报告

```javascript
const reportResponse = await fetch('http://localhost:5000/api/generate-report', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    videoId: '7123456789012345678',
    title: '视频标题',
    config: {
      quantityTrend: true,
      sentimentAnalysis: true,
      sentimentTrend: true,
      wordCloud: true,
      regionDistribution: true
    }
  })
});

const reportData = await reportResponse.json();
console.log(reportData.report);
```

## 10. 注意事项

### 10.1 安全注意事项
1. 所有需要认证的接口必须在请求头中携带有效的token
2. 密码必须加密传输
3. 不要在URL中传递敏感信息
4. 定期更新token

### 10.2 性能注意事项
1. 大数据量分析时建议使用分页
2. 图表数据建议缓存
3. 批量操作建议使用批量接口

### 10.3 兼容性注意事项
1. 所有接口返回JSON格式数据
2. 日期格式统一为ISO 8601标准
3. 字符编码统一使用UTF-8

## 11. 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 完成基础功能开发
- 支持情感分析、趋势分析、词云分析、地区分布分析
- 支持报告生成
