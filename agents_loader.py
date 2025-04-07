import yaml
from agents import Agent
from tools import (
    get_current_date,
    geocode_address,
    query_postgis,
    get_postgis_table_metadata,
    query_postgis_template,
    web_search,
    search_competitor_infomation
)

from info_tools import (
    add_information_initial,
    add_information,
    get_information,
    update_information
)

def load_agents_from_yaml(filepath: str) -> dict:
    """
    Load agent definitions from a YAML file and create Agent instances.
    :param filepath: Path to the YAML file.
    :return: A dictionary {agent_name: Agent instance}
    """
    # 读取配置
    with open(filepath, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)

    tool_mapping = {
    "get_current_date": get_current_date,
    "geocode_address": geocode_address,
    "query_postgis": query_postgis,
    "get_postgis_table_metadata": get_postgis_table_metadata,
    "query_postgis_template": query_postgis_template,
    "web_search": web_search,
    "add_information_initial": add_information_initial,
    "add_information": add_information,
    "get_information": get_information,
    "update_information": update_information,
    "search_competitor_infomation": search_competitor_infomation
    }

    # 构建 agent 实例
    agents = {}
    for agent_name, config in config_dict.items():
        tool_funcs = [tool_mapping[tool] for tool in config.get("tools", []) if tool in tool_mapping]
        agent = Agent(
            name=agent_name,
            model="gpt-4o",
            instructions=config["instructions"],
            tools=tool_funcs
        )
        agents[agent_name] = agent
    return agents
