# Citing SAGE

If you use **SAGE (Safety & Agent Growth Evaluator)**, its benchmark task catalog, evaluation harnesses, or empirical trajectory datasets in your research, please cite our conference publication and software artifact repository.

---

## 1. Academic Publication Citation

### IEEE Format
> P. P. Jain, J. B. Pagare, A. U. Dengale, N. K. Kharat, S. R. Kadam, V. K. Kadam, and SAGE Distributed Study Contributors, "SAGE: Measuring Security Boundary Drift and Capability Retention in Self-Evolving Code Agents," in *Proceedings of the IEEE Conference on Artificial Intelligence and Software Engineering (CAISE)*, 2026. DOI: [10.5281/zenodo.14982104](https://doi.org/10.5281/zenodo.14982104).

### BibTeX Entry
```bibtex
@inproceedings{jain2026sage,
  author    = {Jain, Pratik P. and Pagare, Janhavi B. and Dengale, Aditya U. and Kharat, Naitik K. and Kadam, Shamika R. and Kadam, Vikrant K. and {SAGE Distributed Study Contributors}},
  title     = {{SAGE}: Measuring Security Boundary Drift and Capability Retention in Self-Evolving Code Agents},
  booktitle = {Proceedings of the IEEE Conference on Artificial Intelligence and Software Engineering (CAISE)},
  year      = {2026},
  doi       = {10.5281/zenodo.14982104},
  url       = {https://github.com/Pratikjain24/SAGE},
  keywords  = {autonomous agents, self-evolving code agents, security boundary drift, specification gaming, benchmark, LLM evaluation, capability retention, reward hacking}
}
```

---

## 2. Software Artifact & Dataset Citation

### Software Repository (Zenodo Archive)
```bibtex
@software{sage_software_2026,
  author       = {Jain, Pratik P. and Pagare, Janhavi B. and Dengale, Aditya U. and Kharat, Naitik K. and Kadam, Shamika R. and Kadam, Vikrant K.},
  title        = {{SAGE: Safety \& Agent Growth Evaluator Software Artifact}},
  version      = {1.1.0},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.14982104},
  url          = {https://doi.org/10.5281/zenodo.14982104}
}
```

### Hugging Face Benchmark Dataset (Croissant 1.0)
```bibtex
@dataset{sage_benchmark_dataset_2026,
  author       = {Jain, Pratik P. and {SAGE Evaluation Team}},
  title        = {{SAGE Benchmark Dataset: Tasks, Trajectories, and Human Labels}},
  year         = {2026},
  publisher    = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/Pratikjain24/sage-benchmark}},
  doi          = {10.5281/zenodo.14982104}
}
```

---

## 3. Component Attributions

If you specifically utilize sub-components of SAGE:

* **Benchmark Task Catalog (100 Tasks + 20 Drift Probes)**: Cite the task suite at `tasks/tasks_index.json` (SHA-256: `2bb9569c0756...`).
* **Cryptographic Attestation Ledger**: Cite the immutable SQLite WAL audit trail at `experiments/attestation.db` (57 blocks intact, HMAC-SHA256 verified).
* **Distributed Empirical Trajectories (9,814 Task Episodes)**: Reference the Kaggle study manifest at `experiments/runs/kaggle_study/trajectory_manifest.json` with 0 mock fallbacks across dual Tesla T4 GPUs.
* **Interactive Next.js Dashboard**: Accessible at [Hugging Face Spaces: SAGE-Dashboard](https://huggingface.co/spaces/Pratikjain24/SAGE-Dashboard).

---

## 4. License

The SAGE benchmark framework, task specifications, and trajectories are distributed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for complete terms.
