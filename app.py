from shiny import App, ui, reactive, render
from datetime import datetime
from matplotlib import dates
from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.pyplot as plt
import kpi_calculations

# Create our App
app_ui = ui.page_fluid(
        ui.tags.style("""
            body {
                    font-family: Calibri, sans-serif;
                      background-color: #f4f6f9
            }
            h2  {
                    text-align: center;
                      color: #1a3c5e;
                      margin-top: 20px;
            }
            .kpi-card {
                    background-color: white;
                      border-radius: 8px;
                      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                      padding: 15px;
                      text-align: center;
                      margin: 10px;
            }
            .kpi-label {
                    color: #666;
                      font-size: 14px;
                      margin-bottom: 5px;
            }
            .kpi-value {
                    color: #1a3c5e;
                    font-size: 24px;
                      margin-bottom: 5px;
            }
            .plot-container {
                    background-color: white;
                      border-radius: 8px;
                      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                      padding: 15px;
                      margin: 10px 0;
            }
            .shiny-html-output {
                    border: none !important;
            }              
        """),
        ui.h2("Chocalate Store Sales Dashboard"),

        # KPI Cards
        ui.row(
            ui.column(1, ui.panel_well(ui.h5("Total Revenue"), ui.h3(f"${kpi_calculations.total_revenue:,.0f}"),class_="kpi-card")),
            ui.column(1, ui.panel_well(ui.h5("Total Boxes Sold"), ui.h3(f"{kpi_calculations.total_units:,.0f}"),class_="kpi-card")),
            ui.column(1, ui.panel_well(ui.h5("Total Orders"), ui.h3(f"{kpi_calculations.total_orders:,.0f}"),class_="kpi-card")),
        ),
        ui.row(
            ui.column(2, ui.panel_well(ui.h5("Average Order Value"), ui.h3(f"${kpi_calculations.aov:,.2f}"),class_="kpi-card")),
            ui.column(2, ui.panel_well(ui.h5("Revenue Per Box"), ui.h3(f"${kpi_calculations.rpb:,.2f}"),class_="kpi-card")),
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
            ui.row(
                ui.column(4,
                          ui.div(ui.output_plot("monthly_plot"), class_="plot-container")
                          ),
                ui.column(4,
                          ui.div(ui.output_plot("product_plot"), class_="plot-container")
                          ),
                ui.column(4,
                          ui.div(ui.output_plot("country_plot"), class_="plot-container")
                          ),
            ),

            ui.h3("Sales Leaderboard", style="text-align: center; color: #1a3c5e;"),
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
        fig, ax = plt.subplots(figsize=(6, 3))
        data_in_k = data / 1000
        ax.plot(data.index, data.values, marker="o", color="#e63946", label="Revenue")
        ax.set_title("Monthly Revenue", fontsize=12, color="#1a3c5e")
        ax.set_ylabel("Revenue ($)", fontsize=10)
        ax.xaxis.set_major_formatter(dates.DateFormatter("%b"))
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.legend()
        plt.tight_layout()
        return fig    

    @output
    @render.plot
    def product_plot():
        data = get_filtered_df().groupby("Product")["Amount"].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(6,3))
        data_in_k = data / 1000
        bars = data_in_k.plot.barh(ax=ax, color="royalblue")
        for bar in bars.patches:
            width = bar.get_width()
            ax.text(
                width + 5,
                bar.get_y() + bar.get_height() / 2,
                f'{int(width):,.0f}k',
                ha='left',
                va='center',
                fontsize=8
            )
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}k'))
        max_value = data_in_k.max()
        ax.set_xticks(range(0, int(max_value) + 150,50))
        ax.set_title("Top Ten Products by Revenue", fontsize=12, color="#1a3c5e")
        ax.set_ylabel("Revenue ($)", fontsize=10)
        ax.tick_params(axis='x', labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        plt.tight_layout()
        fig.subplots_adjust(right=0.85)
        return fig  
    
    @output
    @render.plot
    def country_plot():
        data = get_filtered_df().groupby("Country")["Amount"].sum()
        fig, ax = plt.subplots(figsize=(6,3))
        data_in_m = data / 1_000
        bars = data_in_m.plot.bar(ax=ax, color="royalblue")
        for bar in bars.patches:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{int(height)}m',
                ha='center',
                va='bottom',
                fontsize=8
            )
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{int(y)}m'))
        max_value = data_in_m.max()
        ax.set_yticks(range(0, int(max_value) + 250,250))
        ax.set_title("Revenue by Country", fontsize=12, color="#1a3c5e")
        ax.set_xlabel("Country", fontsize=10)
        ax.set_ylabel("Revenue ($m)", fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
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