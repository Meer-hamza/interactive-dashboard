import streamlit as st
import pandas as pd 
import plotly.express as px 
import os 
import warnings
import plotly.figure_factory as ff

warnings.filterwarnings("ignore")

st.set_page_config(page_title="SuperStore!!!!", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: SuperStore less goo")
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# File Upload
f1 = st.file_uploader(":file_folder: Upload File", type=["csv", "txt", "xlsx", "xls"])
if f1 is not None:
    file_ext = os.path.splitext(f1.name)[1]
    if file_ext == '.csv' or file_ext == '.txt':
        df = pd.read_csv(f1)
    else:
        df = pd.read_excel(f1)
else:
    df = pd.read_excel("super.xls")  # default fallback file

# Order Date Handling
df["Order Date"] = pd.to_datetime(df["Order Date"])
startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

col1, col2 = st.columns((2))
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Sidebar Filters
st.sidebar.header("Choose your filter:")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
df2 = df[df["Region"].isin(region)] if region else df.copy()

state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
df3 = df2[df2["State"].isin(state)] if state else df2.copy()

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Final Filter
filtered_df = df3
if city:
    filtered_df = df3[df3["City"].isin(city)]

# Category Sales Bar Chart
category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales",
                 text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Region Pie Chart
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Expandable Data Views
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category View Data"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Category Data", csv, "Category.csv", "text/csv")

with cl2:
    with st.expander("Region View Data"):
        region_df = filtered_df.groupby("Region", as_index=False)["Sales"].sum()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Region Data", csv, "Region.csv", "text/csv")

# Time Series Analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%b"))["Sales"].sum().reset_index()

st.subheader("📈 Time Series Analysis")
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"},
               height=500, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download TimeSeries Data", csv, "TimeSeries.csv", "text/csv")

# Treemap
st.subheader("🌳 Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales",
                  hover_data=["Sales"], color="Sub-Category")
fig3.update_layout(height=650)
st.plotly_chart(fig3, use_container_width=True)

# Pie Charts
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    st.plotly_chart(fig, use_container_width=True)

# Summary Table
st.subheader("📋 Month-wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    sample_df = df.iloc[:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(sample_df, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month-wise Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    pivot_df = pd.pivot_table(filtered_df, values="Sales", index="Sub-Category", columns="month")
    st.write(pivot_df.style.background_gradient(cmap="Blues"))

# Scatter Plot
scatter = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity",
                     title="Relationship between Sales and Profits using Scatter Plot.")
scatter.update_layout(
    xaxis_title="Sales",
    yaxis_title="Profit"
)
st.plotly_chart(scatter, use_container_width=True)

# Final Data View
with st.expander("View Raw Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download original Data
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Original Dataset", data=csv, file_name="Data.csv", mime="text/csv")
