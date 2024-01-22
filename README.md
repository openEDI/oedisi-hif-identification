
# Project Title

A Data-Driven Approach for High-Impedance Fault Localization in Distribution Systems


## Appendix

https://arxiv.org/abs/2311.15168


## Usage/Examples

```javascript
# Pick some high impedance fault data for classification
file_paths = ['IEEE123_PV_L1C1B5HIF.csv', 'IEEE123_PV_L1C1B34HIF.csv', 'IEEE123_PV_L1C1B45HIF.csv']
```

The high impedance fault (HIF) data for the IEEE 123-bus system can be downloaded from [here](https://github.com/yuqingdong0/Transient-Data-for-OEDI/tree/main/Simulation%20Data/IEEE%20123/Faults/High%20Impedance%20Fault). 

The user can select the HIF data from a few locations for the classification. The algorithm first processes the data and apply piecewise linear approximation to the voltage-current trajectory. Following that, the simplified function features are collected as inputs and SVM is utilized for the HIF identification.

