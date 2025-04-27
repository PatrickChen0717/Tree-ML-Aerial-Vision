# Tree-ML-Aerial-Vision
## Overview:
This project trains a machine learning model to classify trees at the canopy level based on aerial images with 15–20 cm pixel resolution. The model performs classification for both **genus** (12 classes) and **species** (17 classes) categories. It uses a **ResNet-18** backbone architecture and is based on methodologies described in the **TreeSatAI** paper.

The training pipeline in this project is modified from the original approach. Specifically, several minority classes are removed, oversampling is applied to address class imbalance, and IBW is also used during training to further balance the learning process. Additionally, data augmentation techniques such as random brightness and hue-saturation adjustments are introduced to mitigate lighting variations in the input images. 

Other techniques, such as a multiresolution pyramid, were also implemented to improve generalization across varying input resolutions. However, this method was ultimately discarded due to limited improvement in generalizability testing and convergence issues during training.


<div style="display: flex; justify-content: space-between;">

<!-- Genus Table -->
<table>
  <thead>
    <tr>
      <th>Genus (Original)</th>
      <th>English Name</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Abies</td><td>Fir</td></tr>
    <tr><td>Acer</td><td>Maple</td></tr>
    <tr><td>Alnus</td><td>Alder</td></tr>
    <tr><td>Betula</td><td>Birch</td></tr>
    <tr><td>Cleared</td><td>Cleared</td></tr>
    <tr><td>Fagus</td><td>Beech</td></tr>
    <tr><td>Fraxinus</td><td>Ash</td></tr>
    <tr><td>Larix</td><td>Larch</td></tr>
    <tr><td>Picea</td><td>Spruce</td></tr>
    <tr><td>Pinus</td><td>Pine</td></tr>
    <tr><td>Pseudotsuga</td><td>Douglas-fir</td></tr>
    <tr><td>Quercus</td><td>Oak</td></tr>
  </tbody>
</table>

<!-- Spacer -->
<div style="width: 40px;"></div>

<!-- Species Table -->
<table>
  <thead>
    <tr>
      <th>Species (Original)</th>
      <th>English Name</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Pinus_sylvestris</td><td>Scots pine</td></tr>
    <tr><td>Fagus_sylvatica</td><td>European beech</td></tr>
    <tr><td>Picea_abies</td><td>Norway spruce</td></tr>
    <tr><td>Cleared</td><td>Cleared</td></tr>
    <tr><td>Quercus_robur</td><td>English oak</td></tr>
    <tr><td>Acer_pseudoplatanus</td><td>Sycamore maple</td></tr>
    <tr><td>Betula_spec.</td><td>Birch species</td></tr>
    <tr><td>Pseudotsuga_menziesii</td><td>Douglas fir</td></tr>
    <tr><td>Fraxinus_excelsior</td><td>European ash</td></tr>
    <tr><td>Quercus_petraea</td><td>Sessile oak</td></tr>
    <tr><td>Alnus_spec.</td><td>Alder species</td></tr>
    <tr><td>Quercus_rubra</td><td>Northern red oak</td></tr>
    <tr><td>Larix_kaempferi</td><td>Japanese larch</td></tr>
    <tr><td>Larix_decidua</td><td>European larch</td></tr>
    <tr><td>Abies_alba</td><td>Silver fir</td></tr>
    <tr><td>Pinus_strobus</td><td>Eastern white pine</td></tr>
    <tr><td>Pinus_nigra</td><td>Black pine</td></tr>
  </tbody>
</table>

</div>


## References:
Paper:

> Ahlswede, S., Schulz, C., Gava, C., Helber, P., Bischke, B., Förster, M., Arias, F., Hees, J., Demir, B., and Kleinschmit, B.: TreeSatAI Benchmark Archive: A multi-sensor, multi-label dataset for tree species classification in remote sensing, Earth Syst. Sci. Data Discuss. [preprint], https://doi.org/10.5194/essd-2022-312, in review, 2022. 

Dataset:
> Schulz, Christian, Ahlswede, Steve, Gava, Christiano, Helber, Patrick, Bischke, Benjamin, Arias, Florencia, Förster, Michael, Hees, Jörn, Demir, Begüm, & Kleinschmit, Birgit. (2022). TreeSatAI Benchmark Archive for Deep Learning in Forest Applications (1.0.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6778154

Original codebase:
> https://git.tu-berlin.de/rsim/treesat_benchmark
