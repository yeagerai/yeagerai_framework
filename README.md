# The Yeager Framework: Embed AI with Domain Expertise
The Yeager Framework is a comprehensive set of tools designed to enable anyone apply their know-how to create AI Experts. By leveraging these tools, you can seamlessly integrate domain-specific knowledge and expertise into a bot powered by generative AI models, such as LLMs (Large Language Models).

The Framework is organized as follows: the `core/` directory houses the essential code and routines for building custom AI Experts, while the `experts/` folder showcases some examples created using these routines.

## Core Features
The Yeager Framework boasts several features that streamline the AI Expert creation process:

- Workflow/Components Framework: This is a crucial element of the Yeager Framework. The workflow/component structure is designed to optimally embed methodological or deterministic knowledge into generative AI models. Picture yourself as a Django expert, a psychologist, or a movie director; you follow a structured, similar process each time, like a methodology for creating a movie.

- Discord Bot Interface: Easily interact with pre-built AI Experts through Discord, which offers a range of features that make it the ideal interface for now.

- GitHub Native Integration: Automatically commit the code generated by AI Experts to GitHub repositories using the callbacks provided in the core.

- LLMs: Currently, the Yeager Framework supports GPT-4, powering our AI Experts with cutting-edge technology. As more LLMs become available, we plan to incorporate them into the framework as well.

Upcoming features:

- yExpertBuilder
- Langchain Integration
- Payments Layer
- Composability Layer
- Automated Testing & Code Improvement

## AI Experts
We are actively developing open-source AI Experts to demonstrate the capabilities of the Yeager Framework. Here are some projects in the pipeline:

### yWorkflows
yWorkflows generates custom workflows based on a text prompt you provide and automatically uploads the entire workflow to GitHub. To use yWorkflows, simply call the `/create` command in our [discord server](https://discord.com/invite/VpfmXEMN66).

You can find a list of all the Community created Workflows [here](https://github.com/search/advanced?q=org%3Ayeagerai+yWorkflows-&type=Repositories)

### yExpertBuilder: (in progress) 
yExpertBuilder creates AI Experts based on a text prompt you provide in the form:

```
{EXPERT NAME}
Description: {Description}
Commands: 
/{command_1}: {description_command_1}
/{command_2}: {description_command_2}
/{command_3}: {description_command_3}
...
```

Once created, the entire AI Expert is uploaded to GitHub. To use yExpertBuilder, call the `/create-expert` command in our [discord server](https://discord.com/invite/VpfmXEMN66).

## Getting Started building with the Yeager Framework
To begin exploring the possibilities of the Yeager Framework, follow these steps:
- Clone or download the repository.
- Navigate through the core/ directory to examine the underlying code and routines.
- Review the examples provided in the experts/ folder to understand how to create AI Experts using the Yeager Framework.
- Join our Discord server to communicate with existing AI Experts and participate in discussions with the developer community.
- Start building your own domain-specific AI Experts by leveraging the tools and features provided in the Yeager Framework.
- Stay updated with the latest features and improvements by following the Yeager Framework's development and engaging with our community.
- Contribute to the project by submitting pull requests, reporting bugs, or suggesting new features and enhancements.

## Why Choose the Yeager Framework?
The Yeager Framework is designed to help developers effortlessly create AI Experts with domain-specific knowledge. By harnessing the power of advanced language models like GPT-4, the framework enables the development of AI Experts that can understand and generate human-like responses. The built-in support for workflow/component structures, Discord bot interfaces, and GitHub native integration make the Yeager Framework a comprehensive solution for AI-driven domain expertise.

Empower AI with your domain expertise using the Yeager Framework and unlock a new world of possibilities. Join us on this exciting journey as we continue to improve and expand the capabilities of the Yeager Framework, shaping the future of AI-driven domain expertise.
