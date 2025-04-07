## File List:
- main.py - main script
- agent_configs.yaml - settings for creating different agent
- agent_loader.py - function for creating agent entity
- tools.py - tools for agent use
- info_tools.py - tools for agents to communicate with each other through MySQL (Other information list function also can be used, MySQL is just a temporary solution)
- db.py - settings for connecting MySQL
- report_template.py - store report template
- md_html.py - convert report from markdown format string to HTML file.

## Overall Framework:
```mermaid
graph LR

    %%{init}%% {
    %% 调整节点对齐方式
    "flowchart": {
        "nodeSpacing": 10,
        "rankSpacing": 40
    }
    }

    %% ===== Subgraph: User Input & Task Preparation =====
    subgraph Task Preparation
        direction TB
        A[User Input] --> B[basic_info_agent<br>获取基础信息]
        A --> D1[report_template] --> D2[report_template_parser_agent<br>拆解模板任务]

        B --> X[basic_info]
        D2 --> E1[Traffic Task]
        D2 --> E2[Location Task]
        D2 --> E3[Competitor Task]
        D2 --> E4[Cost Task]
        D2 --> E5[Consumer Task]

        E1 --> Y[task_list]
        E2 --> Y
        E3 --> Y
        E4 --> Y
        E5 --> Y
    end

    %% ===== Subgraph: Task Execution =====
    subgraph Task_Execution ["Task Execution"]
        direction TB
        X --> F[task_planning_agent<br>任务分配]
        Y --> F

        F --> G1[traffic_analysis_agent]
        F --> G2[location_analysis_agent]
        F --> G3[competitor_analysis_agent]
        F --> G4[cost_analysis_agent]
        F --> G5[consumer_potential_analysis_agent]

        G1 --> T[Task Dictionary]
        G2 --> T
        G3 --> T
        G4 --> T
        G5 --> T

        T --> H[site_selection_report_agent<br>生成报告]
        H --> I[Final Report]
    end

    %% 不可见的连接线用于对齐
    Task Preparation --> Task_Execution
    style Task Preparation fill:none,stroke:none
    style Task_Execution fill:none,stroke:none
```

## Agent List:
|Agent|Task|Tools|Web Search|Status|
|---|---|---|---|---|
|basic_info_agent|Get coordinates, land use, region, POI category, commercial format, date|geocode,spatial query|No|✅Done|
|report_template_parser_agent|Parse report template into detailed subtasks|parser|No|✅Done|
|task_planning_agent|Assign parsed tasks to proper agents|router,registry|No|✅Done|
|traffic_analysis_agent|Count nearby MRT/bus stops, walk distance/time|spatial query|No|✅Done|
|location_analysis_agent|Analyze zoning, district function, suitability|spatial query|Yes|✅Done|
|competitor_analysis_agent|Check nearby competitors, density, brand info|spatial query, google map search|Yes|✅Done|
|cost_analysis_agent|Retrieve rental data and price trend|spatial query|Yes|✅Done|
|consumer_potential_analysis_agent|Estimate population, income, spending power|spatial query|Yes|✅Done|
|site_selection_report_agent|Generate full markdown/HTML report|Markdown to HTML|No|✅Done|


