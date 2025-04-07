import time
from agents import Runner
from agents_loader import load_agents_from_yaml
from report_template import SITE_SELECTION_REPORT_TEMPLATE
from md_html import render_markdown_to_browser

AGENT_REGISTRY = load_agents_from_yaml("agent_configs.yaml")
basic_info_agent = AGENT_REGISTRY["basic_info_agent"]
report_template_parser_agent = AGENT_REGISTRY["report_template_parser_agent"]
task_planning_agent = AGENT_REGISTRY["task_planning_agent"]
traffic_analysis_agent = AGENT_REGISTRY["traffic_analysis_agent"]
location_analysis_agent = AGENT_REGISTRY["location_analysis_agent"]
competitor_analysis_agent = AGENT_REGISTRY["competitor_analysis_agent"]
cost_analysis_agent = AGENT_REGISTRY["cost_analysis_agent"]
consumer_potential_analysis_agent = AGENT_REGISTRY["consumer_potential_analysis_agent"]
site_selection_report_agent = AGENT_REGISTRY["site_selection_report_agent"]

Runner.run_sync(basic_info_agent, "I want to open a new restaurant near Clementi, Singapore. Please help me generate a site selection report.")
tasks = Runner.run_sync(report_template_parser_agent, "I want to open a new restaurant near Clementi, Singapore. Please help me generate a site selection report." + SITE_SELECTION_REPORT_TEMPLATE).final_output
Runner.run_sync(task_planning_agent, tasks)
Runner.run_sync(traffic_analysis_agent, "")
time.sleep(60)
Runner.run_sync(location_analysis_agent, "")
time.sleep(60)
Runner.run_sync(competitor_analysis_agent, "", max_turns=20)
time.sleep(60)
Runner.run_sync(cost_analysis_agent, "")
time.sleep(60)
Runner.run_sync(consumer_potential_analysis_agent, "")
time.sleep(60)
result = Runner.run_sync(site_selection_report_agent, SITE_SELECTION_REPORT_TEMPLATE).final_output

render_markdown_to_browser(result)