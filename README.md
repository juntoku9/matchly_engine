# Matchly Engine

A resume matching tool for HR departments that uses LiteLLM (with OpenAI models) to match resumes to job descriptions.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your OpenAI API key in one of these ways:
   - Create a `.env` file with `OPENAI_API_KEY=your_api_key_here`
   - Set it as an environment variable: `export OPENAI_API_KEY=your_api_key_here`
   - Pass it as a command-line argument

## Usage

1. Place resume PDFs in the `data` folder
2. Run the script:
   ```
   python matchly_engine.py
   ```

3. You can also specify parameters:
   ```
   python matchly_engine.py --data-folder custom_data_folder --job-description "Job description text or path to file" --model "gpt-4-turbo"
   ```

4. Enter the job description when prompted (if not provided as an argument)

5. View the matching results showing ranked resumes with scores

## Example

```
python matchly_engine.py --job-description job_descriptions/data_analyst.txt
```

## About LiteLLM

This tool uses [LiteLLM](https://github.com/BerriAI/litellm) for universal model access. LiteLLM provides a compatible interface for different LLM providers, including OpenAI, Anthropic, Google, and more. By default, it uses OpenAI's models. 