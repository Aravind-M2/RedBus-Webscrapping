# RedBus-Webscrapping
# Transportation Data Analysis  
This project automates data scraping, cleaning, and analysis for bus routes, costs, etc...  

## Features  
- Filter and sort transportation data.  
- Interactive interface using Streamlit.  

## Setup  
1. Install dependencies using `pip install -r requirements.txt`.
2. Run the "Web-scrapping.py" to start scrapping the data from redbus site
3. Run the "Pre-processing_SQL_injection.py" to pre-process the data and inject it into the database 
4. Run the application locally with `streamlit run redbus_Streamlit_app.py` to open the streamlit application to perform analysis filtering and generate reports on scraped redbus data  
## Sample data 
1.copy the files in sample data and paste in the same path as .py files( or same path as .ipynb files - if you are going to use .ipynb files ) 
2.run the "Pre-processing_SQL_injection.py" to pre-process the data(previously collected) and inject it into the database
  (this data is for sample)
## Future Enhancements  
- Integration with remote databases and advanced visualizations.

## How to use the streamlit app
- select the required columns from required columns multiselect box
- Add or remove filters using the manage filters area on the left pane
- Sort the data using the sort options available on the top left area of the left pane
- Click on the run button to apply the filters and generate the report
- Click on the next button to go to the next pages and previous to go the previous pages
- Click on the Download filtered data button to download the generated report
- Use the appropriate logical conditions for selected columns to filter without errors. error handlings on filters and more enhancements will be added in the future
-----------------------------------------------------------------------------------------------------
## Project report
"Redbus_mini_project_report.pdf" will have the overall project report
- open it with edge if it does not open properly with adobe acrobat
- click on this link for interactive slides **https://gamma.app/docs/Redbus-mini-project-report-k0sea0thgjd7hug**
