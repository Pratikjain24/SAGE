# Citing SAGE

If you use **SAGE (Safety & Agent Growth Evaluator)**, its benchmark task catalog, evaluation harnesses, or empirical trajectory datasets in your research or project, please cite the software repository and benchmark dataset:

---

## 1. Software Repository Citation (Zenodo & GitHub)

```bibtex
@software{sage_software_2026,
  author       = {Jain, Pratik P. and Pagare, Janhavi B. and Dengale, Aditya U. and Kharat, Naitik K. and Kadam, Shamika R. and Kadam, Vikrant K.},
  title        = {{SAGE: Safety \& Agent Growth Evaluator — Empirical Evaluation Framework for Self-Evolving Code Agents}},
  version      = {1.1.0},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.14982104},
  url          = {https://github.com/Pratikjain24/SAGE}
}
```

---

## 2. Hugging Face Benchmark Dataset (Croissant 1.0)

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

* **Benchmark Task Catalog (100 Tasks + 20 Drift Probes)**: Located at [`tasks/tasks_index.json`](tasks/tasks_index.json).
* **Cryptographic Attestation Ledger**: Immutable SQLite WAL audit trail at `experiments/attestation.db` (57 blocks intact, HMAC-SHA256 verified).
* **Distributed Empirical Trajectories (9,800 Canonical Task Evaluations)**: Manifested in [`experiments/runs/kaggle_study/MANIFEST.sha256`](experiments/runs/kaggle_study/MANIFEST.sha256) across Dual Tesla T4 GPUs with zero mock fallbacks.
* **Interactive Next.js Web Observatory**: Accessible locally via `start_dashboard.bat` and hosted on [Hugging Face Spaces](https://huggingface.co/spaces/Pratikjain24/SAGE-Dashboard).

---

## 4. License

The SAGE benchmark framework, task specifications, and trajectories are distributed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for complete terms.
