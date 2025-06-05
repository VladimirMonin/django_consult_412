## Brief overview
These rules outline an effective strategy for searching and retrieving documentation for "Cline" (or similar libraries) using the Context7 MCP tool. This approach is designed to be systematic and help even less experienced models or users to find relevant information efficiently. This is a global set of guidelines applicable to any task involving Context7 documentation search.

## Step 1: Obtain Exact Library ID
- **Action:** Always start by using the `resolve-library-id` tool.
- **Parameter:** Set `libraryName` to "Cline" (or the target library, e.g., "React", "Python requests").
- **Rationale:** This provides the precise `context7CompatibleLibraryID` (e.g., `/cline/cline`), which is crucial for accurate subsequent documentation queries. Without the correct ID, searches may fail or return irrelevant information.

## Step 2: Request General Documentation Overview
- **Action:** After obtaining the ID, use the `get-library-docs` tool for an initial broad query.
- **Parameters:**
    - `context7CompatibleLibraryID`: Use the ID obtained in Step 1.
    - `userQuery`: Ask a very general question, e.g., "Cline documentation overview", "[Library Name] introduction", or "What is [Library Name]?".
- **Rationale:** This helps to get a foundational understanding of the documentation's scope, main topics, and overall structure before diving into specifics.

## Step 3: Detail Queries by Topic
- **Action:** Avoid trying to find everything with a single, overly complex query. Break down the information need into smaller, topical queries using `get-library-docs`.
- **Parameters:**
    - `context7CompatibleLibraryID`: Use the same ID from Step 1.
    - `topic`: Specify a relevant topic based on the initial overview or known areas of interest. Examples include:
        - `tool usage` (for tools like Cline)
        - `API reference`
        - `configuration`
        - `getting started`
        - `installation`
        - `best practices`
        - `security`
        - `examples`
    - `userQuery`: Formulate a question corresponding to the topic. For instance, if `topic: "configuration"`, `userQuery` could be "How to configure [Feature X] in [Library Name]".
- **Rationale:** Topical queries yield more focused, manageable, and relevant sets of results, making it easier to find specific details.

## Step 4: Utilize Keywords from Previous Responses
- **Action:** Carefully review the titles (TITLE) and descriptions (DESCRIPTION) in the results from previous queries. If specific terms, feature names, or module names appear frequently (e.g., `.clinerules`, `new_task` for Cline; `useState`, `useEffect` for React), incorporate them into subsequent `userQuery` values.
- **Example:** If documentation for Cline repeatedly mentions `.clinerules`, a follow-up `userQuery` could be "Detailed guide for .clinerules in Cline".
- **Rationale:** This aligns the search with the documentation's own terminology and structure, significantly improving search precision and relevance.

## Step 5: Iterate and Refine Queries
- **Action:** If an initial topical query does not provide the necessary information, or if it returns too much general content, try rephrasing the `userQuery` to be more specific, or select a slightly different or more granular `topic`.
- **Example:** If `userQuery: "Cline tools"` is too broad, refine it to `userQuery: "XML example for write_to_file tool in Cline"` or `userQuery: "Advanced usage of search_files tool in Cline"`.
- **Rationale:** Searching is often an iterative process. Multiple, refined attempts with varied phrasing or focus are more effective than a single, broad, and potentially unsuccessful one.

## Step 6: Be Persistent (Make "Many Requests" if Necessary)
- **Action:** As per user guidance during the initial documentation gathering for Cline, do not hesitate to make multiple requests if the information is complex or spread out. If a topic is not fully covered by one query, approach it from different angles or break it down into even smaller sub-topics.
- **Rationale:** A comprehensive understanding or a complete set of information is often built from several targeted queries rather than a single attempt. This is especially true for extensive documentation.

## Simplified Example Sequence (for Cline)
- 1. `resolve-library-id` with `libraryName: "Cline"` to get ID (e.g., `/cline/cline`).
- 2. `get-library-docs` with ID `/cline/cline`, `userQuery: "Cline overview"`.
- 3. `get-library-docs` with ID `/cline/cline`, `topic: "tool usage"`, `userQuery: "How to use tools in Cline"`.
- 4. `get-library-docs` with ID `/cline/cline"`, `topic: "configuration"`, `userQuery: "How to configure Cline"`.
- 5. `get-library-docs` with ID `/cline/cline"`, `topic: "prompting"`, `userQuery: "Cline prompting guide"`.
- 6. `get-library-docs` with ID `/cline/cline"`, `topic: "MCP"`, `userQuery: "Cline MCP information"`.
