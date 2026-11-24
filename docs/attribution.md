# Sources and third-party assets

Original application code, written documentation, generated control images and architecture diagrams carry the requested Imarah.tech notice. Third-party work keeps its original ownership and licence.

## Project inputs

- [The team's FYP proposal](<../FYP-I-project-proposal-2026-final (1).pdf>), dated 18 September 2026: modules, scope, team responsibilities and timeline.
- [The supplied VLM shortlist](<../Extra-Documentations/FYP VLM List & Download Commands.docx>): candidate models and training/inference plans.
- The original saved `Phase1.md` was empty. The updated document states this instead of inventing an endpoint.

## Models and data

- Official Hugging Face [SmolVLM 256M](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) and [500M](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct) checkpoints: Apache-2.0 model cards; downloaded repository metadata is kept in each local folder.
- [CrackForest](https://github.com/cuilimeng/CrackForest-dataset): two unchanged road photographs, non-commercial research use only. Full citation and limits are in [fixture sources](../benchmarks/fixtures/SOURCES.md).
- [Cracked wall 03.jpg](https://commons.wikimedia.org/wiki/File:Cracked_wall_03.jpg) by Almanta: one unchanged interior-wall photograph, CC BY-SA 4.0. The image keeps its own licence, with credit displayed in the app and retained in new reports.
- The original larger model shortlist stays linked in [models/README.md](../models/README.md). A registry entry is not evidence that a model was installed or evaluated.

## Interface assets

- The building mark and architectural line illustration are original code-drawn Imarah assets.
- [Lucide](https://lucide.dev/) provides UI icons under its ISC licence, retained in the installed package.
- [DM Sans](https://github.com/google/fonts/tree/main/ofl/dmsans) and [Manrope](https://github.com/google/fonts/tree/main/ofl/manrope) are served locally under the SIL Open Font License. Notices are included in `frontend/public/fonts/`.

## Technical references consulted

- [Vite guide](https://vite.dev/guide/) for the frontend toolchain.
- [FastAPI request files](https://fastapi.tiangolo.com/tutorial/request-files/) for file-upload handling.
- [Official SmolVLM model cards](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) for processor/model inference usage.
- [Ollama vision API](https://docs.ollama.com/capabilities/vision) for base64 image chat requests.
- [Qwen3-VL on Ollama](https://ollama.com/library/qwen3-vl:2b) for the required runtime version.
- [Ultralytics documentation](https://docs.ultralytics.com/platform/) for the trained-model integration context. The supplied endpoint's contract and authenticated image requests were verified; see [YOLO findings](evaluation/yolo-findings.md).

Python and JavaScript dependencies retain their distributed licences. The project lockfiles/configuration identify the selected package versions; the Imarah licence does not replace dependency licences.
