from shiny import App, ui, reactive, render
import pandas as pd
import matplotlib.pyplot as plt
import kpi_calculations

# Load & Clean Data
df = pd.read_csv("Chocolate Sales.csv")
df["Date"]   = pd.to_datetime(df["Date"], format="%d-%b-%y")
df["Amount"] = df["Amount"].str.replace(r"[\$,]", "", regex=True).astype(float)

# Create our App
app_ui = ui.page_fluid(
        ui.h2("Chocalate Store Sales Dashboard"),

        # KPI Cards
        ui.row(
            ui.column(4, ui.panel_well(ui.h5("Total Revenue"), ui.h3(f"${kpi_calculations.total_revenue:,.2f}"))),
            ui.column(4, ui.panel_well(ui.h5("Total Boxes Sold"), ui.h3(f"${kpi_calculations.total_units:,.2f}"))),
            ui.column(4, ui.panel_well(ui.h5("Total Orders"), ui.h3(f"${kpi_calculations.total_orders:,.2f}"))),
        ),
        ui.row(
            ui.column(6, ui.panel_well(ui.h5("Average Order Value"), ui.h3(f"${kpi_calculations.aov:,.2f}"))),
            ui.column(6, ui.panel_well(ui.h5("Revenue Per Box"), ui.h3(f"${kpi_calculations.rpb:,.2f}"))),
        )
)

def server(input,output,session):
    pass
    
app = App(app_ui, server)
if __name__ == "__main__":
    # Serving on 127.0.0.1:8000 with automatic reload on code changes
    app.run(host="127.0.0.1", port=8000)