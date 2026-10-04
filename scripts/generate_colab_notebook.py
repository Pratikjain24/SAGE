import json
from pathlib import Path

notebook = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {"name": "SAGE_Colab_Benchmark.ipynb", "provenance": []},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"}
    },
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# SAGE: Autonomous Code Agent Evolution Benchmark\n",
                "### Official 1-Click Interactive Cloud Benchmark Runner\n",
                "\n",
                "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pratikjain24/SAGE/blob/main/SAGE_Colab_Benchmark.ipynb)\n",
                "\n",
                "This notebook executes SAGE live empirical evaluations on Google Colab (Free T4 GPU / High-RAM CPU), measuring Safety Drift, Specification Gaming, and Capability Retention across all 7 Agent Archetypes (G1-G7) over 5 evolutionary cycles."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Step 1: Clone Repository & Setup Environment"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 1. Clone repository directly into Colab\n",
                "!rm -rf /content/sage\n",
                "!git clone https://github.com/Pratikjain24/SAGE.git /content/sage\n",
                "\n",
                "# 2. Navigate and install dependencies\n",
                "%cd /content/sage\n",
                "!pip install -q --upgrade pip\n",
                "!pip install -q -e .\n",
                "print(\"\\n✅ SAGE Framework Installed Successfully!\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Step 2: Configure API Key & Model (Groq / OpenRouter / OpenAI)"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "try:\n",
                "    from google.colab import userdata\n",
                "    api_key = userdata.get('GROQ_API_KEY')\n",
                "except Exception:\n",
                "    api_key = None\n",
                "\n",
                "# Paste your Groq API key below or set it in Colab Secrets\n",
                "GROQ_API_KEY = \"your_groq_api_key_here\" #@param {type:\"string\"}\n",
                "key_to_use = api_key or GROQ_API_KEY\n",
                "\n",
                "os.environ[\"GROQ_API_KEY\"] = key_to_use\n",
                "os.environ[\"OPENAI_API_BASE\"] = \"https://api.groq.com/openai/v1\"\n",
                "os.environ[\"OPENAI_API_KEY\"] = key_to_use\n",
                "print(f\"✅ Configured API Endpoint with Key: {key_to_use[:8]}...{key_to_use[-4:] if len(key_to_use) > 12 else ''}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Step 3: Run Full Live Empirical Benchmark (All 7 Archetypes, 5 Cycles)"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Run all 7 archetypes (G1-G7) across 5 cycles on live model (qwen3.8-27b)\n",
                "!python scripts/run_real_experiment.py \\\n",
                "    --config configs/experiments/real_groq_strict.yaml \\\n",
                "    --run-id colab_empirical_study \\\n",
                "    --groups G1,G2,G3,G4,G5,G6,G7 \\\n",
                "    --cycles 5 \\\n",
                "    --seeds 42 \\\n",
                "    --train 20 \\\n",
                "    --test 10"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Step 4: Generate Publication LaTeX Tables & Figures"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Recompute metrics, generate publication plots and export LaTeX tables\n",
                "!python -m sage.runner.cli analyze --run-id colab_empirical_study --recompute\n",
                "!python -m sage.runner.cli stats --run-id colab_empirical_study\n",
                "\n",
                "print(\"\\n======================================================\")\n",
                "print(\"TABLE 1 (Main Evolutionary Results):\")\n",
                "print(\"======================================================\")\n",
                "!cat paper/tables/table1_main_results.tex\n",
                "\n",
                "print(\"\\n======================================================\")\n",
                "print(\"TABLE 3 (Statistical Significance Matrix):\")\n",
                "print(\"======================================================\")\n",
                "!cat paper/tables/table3_top8_significance.tex"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Step 5: Download Trajectory & Publication Assets (.zip)"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import shutil\n",
                "from google.colab import files\n",
                "\n",
                "# Package figures, tables, and trajectory into zip\n",
                "shutil.make_archive(\"/content/SAGE_Colab_Results\", \"zip\", \"/content/sage/experiments/runs/colab_empirical_study\")\n",
                "print(\"✅ Download starting for SAGE_Colab_Results.zip...\")\n",
                "files.download(\"/content/SAGE_Colab_Results.zip\")"
            ]
        }
    ]
}

root = Path(__file__).resolve().parent.parent
with open(root / "SAGE_Colab_Benchmark.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print("Created sanitized SAGE_Colab_Benchmark.ipynb successfully!")
