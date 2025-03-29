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
    A[User Input] --> B[basic_info_agent - 获取坐标/业态/区域信息]
    B --> C[Task Dictionary]

    subgraph Report Template Parsing
        D[report_template_parser_agent - 拆解模板任务]
        D --> E1[Traffic Task]
        D --> E2[Location Task]
        D --> E3[Competitor Task]
        D --> E4[Cost Task]
        D --> E5[Consumer Task]
    end

    D --> F[task_planning_agent - 任务分配]
    F --> G1[traffic_analysis_agent]
    F --> G2[location_analysis_agent]
    F --> G3[competitor_analysis_agent]
    F --> G4[cost_analysis_agent]
    F --> G5[consumer_potential_analysis_agent]

    G1 --> C
    G2 --> C
    G3 --> C
    G4 --> C
    G5 --> C

    C --> H[site_selection_report_agent - 生成报告]
    H --> I[Final Report]
```

Agent List:


