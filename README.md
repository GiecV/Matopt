# Mathematical Optimization Project

This project is the final project for the Mathematical Optimization exam. It aims to reproduce the results of [A fix-and-optimize heuristic for the Unrelated Parallel Machine Scheduling Problem](https://www.sciencedirect.com/science/article/pii/S0305054823003684?fr=RR-2&ref=pdf_download&rr=88a44f584c310e11), by:
- George H.G. Fonseca
- Guilherme B. Figueiroa 
- Túlio A.M. Toffolo

## Description

This project focuses on the implementation and analysis of the mathematical optimization techniques described in the aforementioned paper. In detail, the paper presents two exact formulations of the problem and a fix-and-optimize heuristic.

## Run the Project

Run `run.ipynb` for trying all the methods proposed by the paper with a fixed instance.

The project uses the WLS license for Gurobi, which means that you have to get your own license, put the three lines in a text file and rename it `credentials.txt`.

`Scalability.py` and `Scalability_heuristic.py` are used to perform some tests on the model

`cuts_analysis.ipynb` contains information about the creation of the cuts in the Master problem