# Example Script for Creating Parameterized Models with Abaqus  

This script serves as a reference for creating parameterized models in Abaqus. It generates a model of a reinforced concrete plate with a hole positioned at an arbitrary location.  

The plate is fixed on the left side as an essential boundary condition, and loaded by an uniform pressure applied to the top surface.  
### Adjustable Parameters  
The following parameters can be modified:  
- **Plate dimensions**: width, height, and thickness  
- **Hole properties**: location and diameter  
- **Reinforcement**: spacing and diameter of the rebars  
- **Loading**: pressure magnitude  

## Execution Instructions  
### Within the GUI  
Navigate to **File** → **Run Script...** → **main.py**  

### From the Command Line  
Run the following command:  
```bash
abaqus cae noGUI=main.py  
