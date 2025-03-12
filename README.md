# Example Script for Creating Parameterized Models with Abaqus  

This script serves as a reference for creating parameterized models in Abaqus. It generates a model of a reinforced concrete plate with a hole positioned at an arbitrary location.  

The plate is fixed on the left side as an essential boundary condition and loaded by a uniform pressure applied to the top surface.

---
> **Note**  
> The **"geo"** folder contains the code responsible for parametrization, logic, and geometry definition, while the **"abq"** folder contains the code for generating the corresponding Abaqus model.  
>  
> **Workflow:**  
> 1. A geometry model is created using the code in the **"geo"** folder.  
> 2. This model is then passed to the **AbaqusModelFactory** in the **"abq"** folder.  
> 3. The factory generates the corresponding Abaqus model.  
>
> Since the geometry is defined separately, Abaqus licenses are only required for the final model creation in the **AbaqusModelFactory**.  

---

### Adjustable Parameters  
The following parameters can be modified:  
- **Plate dimensions**: width, height, and thickness  
- **Hole properties**: location and diameter  
- **Reinforcement**: spacing and diameter of the rebars  
- **Loading**: pressure magnitude  
- **Mesh size**: C3D20 elements for the plate and B32 for the rebars

## Execution Instructions  
### Within the GUI  
Navigate to **File** → **Run Script...** → **main.py**  

### From the Command Line  
Run the following command:  
```bash
abaqus cae noGUI=main.py  
