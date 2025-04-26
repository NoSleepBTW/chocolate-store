from shiny import App, ui, reactive, render
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import kpi_calculations

# Create our App
app_ui = ui.page_fluid(
        ui.h2("Chocalate Store Sales Dashboard"),

        # KPI Cards
        ui.row(
            ui.column(1, ui.panel_well(ui.h5("Total Revenue"), ui.h3(f"${kpi_calculations.total_revenue:,.0f}"))),
            ui.column(1, ui.panel_well(ui.h5("Total Boxes Sold"), ui.h3(f"{kpi_calculations.total_units:,.0f}"))),
            ui.column(1, ui.panel_well(ui.h5("Total Orders"), ui.h3(f"{kpi_calculations.total_orders:,.0f}"))),
        ),
        ui.row(
            ui.column(2, ui.panel_well(ui.h5("Average Order Value"), ui.h3(f"${kpi_calculations.aov:,.2f}"))),
            ui.column(2, ui.panel_well(ui.h5("Revenue Per Box"), ui.h3(f"${kpi_calculations.rpb:,.2f}"))),
        ),

        # Sidebar + Main area for plots
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select("product", "Product:",
                                choices=["All"] + sorted(kpi_calculations.df["Product"].unique()),
                                selected="All"),
                ui.input_select("country", "Country:",
                                choices=["All"] + sorted(kpi_calculations.df["Country"].unique()),
                                selected="All"),
                ui.input_date_range("daterange","Date Range:",
                                start=kpi_calculations.df["Date"].min(),
                                end=kpi_calculations.df["Date"].max())  
            ),
            ui.output_plot("monthly_plot"),
            ui.output_plot("product_plot"),
            ui.output_plot("country_plot"),

            ui.h3("Sales Leaderboard"),
            ui.output_table("leaderboard_table")

        )
)

def server(input,output,session):
    
    def get_filtered_df():
        df = kpi_calculations.df
        start, end = input.daterange()
        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end + pd.Timedelta(days=1), datetime.min.time())

        # Date Filter
        condition = (df["Date"] >= start) & (df["Date"] < end)

        # Apply filter if "All" not selected
        if input.product() != "All":
            condition = condition & (df["Product"] == input.product())

        if input.country() != "All":
            condition = condition & (df["Country"] == input.country())

        return df[condition]

    @output
    @render.plot
    def monthly_plot():
        df_filt = get_filtered_df().set_index("Date")
        data = df_filt.resample("ME")["Amount"].sum()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(data.index, data.values, marker="o")
        ax.set_title("Monthly Revenue")
        ax.set_ylabel("Revenue ($)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig    

    @output
    @render.plot
    def product_plot():
        data = get_filtered_df().groupby("Product")["Amount"].sum().nlargest(5)
        fig, ax = plt.subplots(figsize=(6,4))
        data.plot.bar(ax=ax)
        ax.set_title("Top Five Products by Revenue")
        ax.set_ylabel("Revenue ($)")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        return fig  
    
    @output
    @render.plot
    def country_plot():
        data = get_filtered_df().groupby("Country")["Amount"].sum().nlargest(5)
        fig, ax = plt.subplots(figsize=(6,4))
        data.plot.bar(ax=ax)
        ax.set_title("Top Five Countries by Revenue")
        ax.set_ylabel("Revenue ($)")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        return fig
    
    @output
    @render.table
    def leaderboard_table():
        tbl = (get_filtered_df().groupby("Sales Person")["Amount"].sum().nlargest(10).reset_index(name="Revenue"))
        tbl["Revenue"] = tbl["Revenue"].map(lambda x: f"${x:,.2f}")
        return tbl
    
    def download_data():
        df = get_filtered_df()
        return {
            "content": df.to_csv(index=False).encode("utf-8"),
            "filename": "filtered_chocolate_sales.cvs",
            "mimetype": "text/csv",
        }


app = App(app_ui, server)
if __name__ == "__main__":
    # Serving on 127.0.0.1:8000 with automatic reload on code changes
    app.run(host="127.0.0.1", port=8000)