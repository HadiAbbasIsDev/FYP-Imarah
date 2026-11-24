# Image sources and limits

The original comparison set contains two research photographs and two generated controls. A separate interior-wall photograph was added during the Qwen continuation. The app exposes image type and keeps the original four-image comparison selectable.

## CrackForest photographs

`crackforest-001.jpg` and `crackforest-003.jpg` were downloaded unchanged from the [CrackForest dataset repository](https://github.com/cuilimeng/CrackForest-dataset), using files `image/001.jpg` and `image/003.jpg`. The source README permits **non-commercial research purposes only**. These images retain the dataset's terms; the Imarah.tech all-rights-reserved notice does not apply to them.

Requested citation:

Yong Shi, Limeng Cui, Zhiquan Qi, Fan Meng and Zhensong Chen. “Automatic road crack detection using random structured forests.” *IEEE Transactions on Intelligent Transportation Systems*, 17(12), 3434–3445, 2016.

The dataset also lists: Limeng Cui, Zhiquan Qi, Zhensong Chen, Fan Meng and Yong Shi. “Pavement Distress Detection Using Random Decision Forests.” *International Conference on Data Science*, 95–102, 2015.

These are **road-surface images**, not building photographs. They support a small inference demonstration, not claims about building safety or building-domain performance. No ground-truth detection boxes or segmentation scores are claimed for this sample set.

## Synthetic images

`synthetic-intact.jpg` is a seeded textured surface. `synthetic-crack.jpg` is the same surface with a branching line drawn by `scripts/prepare_fixtures.py`. Both are original Imarah.tech test assets and are explicitly labelled synthetic.

Only `synthetic-crack` has a manually specified illustrative bounding region in the sample manifest. Its confidence is `null`, because no detector predicted it. The benchmark passes original images, not that overlay, to the VLM.

`manifest.json` retains each source, type, description and SHA-256 hash. The app makes a cleaned JPEG copy when a sample is used as an inspection; benchmark hashes refer to the original fixture files.

## Interior-wall photograph

`commons-wall-03.jpg` is **Cracked wall 03.jpg**, photographed by **Almanta** on 28 December 2022 and published on [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Cracked_wall_03.jpg). It is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). The original 4,624 × 2,600 photograph is stored unchanged, with SHA-256 `860e7aeefde938e85e4c1966eb051d22449c6c1cbccdac53cd615fa9d0b12eb5`.

The image shows an interior wall beside a floor and skirting board. The supplied caption describes a crack in an old guest house. We have no on-site assessment, calibrated scale, labelled detection boxes, or evidence about the cause or safety of this wall. This is one convenience example for examining model descriptions, not a held-out building dataset.

The image and any resized/re-encoded inspection copies retain CC BY-SA 4.0. The Imarah all-rights-reserved notice applies to our original code, not this photograph. The app shows the author, source and licence beside the selected photo, in the model lab and in new inspection reports. New inspection exports preserve the attribution and note their resizing, JPEG encoding and metadata removal. Keep that credit with any shared image or report.

`building-samples.json` stores the pinned source and attribution used by the preparation script. The original four-image experiment remains unchanged; select **Building photograph · exploratory** to run this new example separately.
