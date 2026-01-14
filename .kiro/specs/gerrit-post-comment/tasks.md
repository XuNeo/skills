# Implementation Plan: Gerrit Post Comment

## Overview

实现 `post_comment.py` 脚本，为 gerritcomment skill 添加发布评论功能。采用增量开发方式，先实现核心功能，再添加高级特性。

## Tasks

- [x] 1. 创建基础脚本结构
  - 创建 `skills/gerritcomment/scripts/post_comment.py`
  - 复用 `get_comments.py` 中的 `parse_change_url()`, `get_config()`, `GerritError`
  - 设置基本的 argparse CLI 框架
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. 实现 ReviewInput 构建函数
  - [x] 2.1 实现 `build_review_input()` 函数
    - 支持 message, tag, labels, comments 参数
    - 返回符合 Gerrit API 规范的字典
    - _Requirements: 1.1, 5.1, 6.1_
  - [x] 2.2 编写 ReviewInput 属性测试
    - **Property 1: ReviewInput message construction**
    - **Property 6: ReviewInput labels construction**
    - **Property 7: ReviewInput tag construction**
    - **Validates: Requirements 1.1, 5.1, 6.1**

- [x] 3. 实现 CommentInput 构建函数
  - [x] 3.1 实现 `build_comment_input()` 函数
    - 支持 message, line, range_, in_reply_to, unresolved, side 参数
    - 实现 unresolved 默认值逻辑
    - _Requirements: 2.1, 2.2, 3.1, 4.1, 4.2, 4.3_
  - [x] 3.2 编写 CommentInput 属性测试
    - **Property 2: CommentInput file and line construction**
    - **Property 3: CommentInput range construction**
    - **Property 4: CommentInput reply construction**
    - **Property 5: CommentInput unresolved flag handling**
    - **Validates: Requirements 2.1, 2.2, 3.1, 4.1, 4.2, 4.3**

- [x] 4. Checkpoint - 确保构建函数测试通过
  - 运行所有属性测试
  - 确保所有测试通过，如有问题请询问用户

- [x] 5. 实现 post_review 核心函数
  - [x] 5.1 实现 `post_review()` 函数
    - 使用 GerritClient 连接服务器
    - 调用 `revision.set_review()` API
    - 处理 HTTP 错误并转换为 GerritError
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [x] 5.2 实现输出格式化
    - 成功时返回 JSON 包含 change, revision, success
    - 失败时返回 JSON 包含 change, revision, error
    - _Requirements: 8.1, 8.2, 8.3_
  - [x] 5.3 编写输出格式属性测试
    - **Property 9: Output format consistency**
    - **Validates: Requirements 8.1, 8.2, 8.3**

- [x] 6. 实现 CLI 参数解析
  - [x] 6.1 添加基本参数
    - --change (必需)
    - --revision (可选)
    - --message (可选)
    - --tag (可选)
    - _Requirements: 1.1, 1.2, 1.3, 6.1_
  - [x] 6.2 添加行内评论参数
    - --file (可选)
    - --line (可选)
    - --range (可选, JSON)
    - --reply-to (可选)
    - --unresolved/--resolved (可选)
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 4.1, 4.2_
  - [x] 6.3 添加投票参数
    - --labels (可选, JSON)
    - _Requirements: 5.1_

- [x] 7. 实现批量评论功能
  - [x] 7.1 添加 --comments-json 参数
    - 支持 JSON 字符串或 @file 路径
    - 解析并验证 JSON 结构
    - _Requirements: 7.1, 7.2, 7.3_
  - [x] 7.2 编写批量评论属性测试
    - **Property 8: Batch comments parsing round-trip**
    - **Validates: Requirements 7.1**

- [x] 8. 实现 main 函数
  - 整合所有组件
  - 处理参数组合逻辑
  - 输出 JSON 结果
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 9. Checkpoint - 确保所有测试通过
  - 运行所有单元测试和属性测试
  - 确保所有测试通过，如有问题请询问用户

- [x] 10. 更新 SKILL.md 文档
  - 添加 post_comment.py 的使用说明
  - 添加参数说明和示例
  - 添加输出格式说明
  - _Requirements: 所有_

## Notes

- All tasks are required for comprehensive implementation
- 使用 Python 3.9+ 语法
- 测试框架：pytest + hypothesis
- 属性测试最少运行 100 次迭代
