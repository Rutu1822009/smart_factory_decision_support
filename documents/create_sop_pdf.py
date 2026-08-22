from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

pdf_path = "Machine_Maintenance_SOP.pdf"

doc = SimpleDocTemplate(pdf_path, pagesize=A4)

styles = getSampleStyleSheet()
story = []

text = """
<b>MACHINE MAINTENANCE SOP</b><br/><br/>

<b>1. Purpose</b><br/>
This SOP explains the basic maintenance procedure for manufacturing machines.<br/><br/>

<b>2. Safety Precautions</b><br/>
- Switch off the machine before maintenance.<br/>
- Disconnect the power supply.<br/>
- Wear required safety equipment.<br/>
- Do not touch moving parts during maintenance.<br/><br/>

<b>3. Daily Inspection</b><br/>
- Check machine power connection.<br/>
- Check abnormal noise or vibration.<br/>
- Check oil and lubrication levels.<br/>
- Check machine temperature.<br/>
- Clean the machine working area.<br/><br/>

<b>4. Maintenance Procedure</b><br/>
Step 1: Stop the machine.<br/>
Step 2: Disconnect the power supply.<br/>
Step 3: Inspect machine components.<br/>
Step 4: Check lubrication.<br/>
Step 5: Check belts and connections.<br/>
Step 6: Clean the machine.<br/>
Step 7: Restart and test the machine.<br/><br/>

<b>5. Maintenance Frequency</b><br/>
Daily: Visual inspection and cleaning.<br/>
Weekly: Lubrication and component inspection.<br/>
Monthly: Detailed maintenance and calibration check.<br/><br/>

<b>6. Emergency Condition</b><br/>
If abnormal noise, excessive vibration, overheating or sudden machine failure is observed, stop the machine immediately and inform the maintenance supervisor.<br/><br/>

<b>7. Responsible Person</b><br/>
Maintenance Technician and Production Supervisor are responsible for maintenance activities.
"""

story.append(Paragraph(text, styles["Normal"]))
story.append(Spacer(1, 12))

doc.build(story)

print("PDF created successfully!")