import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Global Investment in AI Dashboard",
    page_icon="💴",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

df_reshaped = pd.read_csv('data.csv')

df_reshaped = df_reshaped.rename(columns={
    'Entity': 'country',
    'Code': 'country_code',
    'Year': 'year',
    'Global total private investment in AI': 'investment'
})

with st.sidebar:
    st.title('Investments in AI Dashboard')

    year_list = list(df_reshaped.year.unique())[::-1]

    selected_year = st.selectbox(
        'Select a year', year_list, index=len(year_list)-1)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(
        by="investment", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno',
                        'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox(
        'Select a color theme', color_theme_list)


def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18,
                titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(
            title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'max({input_color}):Q',
                        legend=None,
                        scale=alt.Scale(scheme=input_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=900
                 ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )
    # height=300
    return heatmap


def make_choropleth(input_df, input_id, input_column, input_color_theme):
    map_df = input_df[input_df[input_id].notna() &
                      (input_df[input_id] != 'OWID_WRL') &
                      (input_df['country'] != 'Europe')]

    choropleth = px.choropleth(map_df, locations=input_id, color=input_column, locationmode="ISO-3",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(map_df[input_column]) if len(
                                   map_df) > 0 else 1),
                               labels={input_column: 'AI Investment (USD)'}
                               )
    choropleth.update_layout(
        template='simple_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        geo=dict(
            bgcolor='white',
            lakecolor='#E8F4FD',
            landcolor='#F5F5F5',
            coastlinecolor='#CCCCCC',
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

col = st.columns((6, 2), gap='medium')

with col[0]:
    st.markdown('#### Total Investments')

    choropleth = make_choropleth(
        df_selected_year, 'country_code', 'investment', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

    heatmap = make_heatmap(df_reshaped, 'year', 'country',
                           'investment', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

with col[1]:
    st.markdown('#### Top Countries')

    st.dataframe(df_selected_year_sorted,
                 column_order=("country", "investment"),
                 hide_index=True,
                 column_config={
                     "country": st.column_config.TextColumn(
                         "Country",
                     ),
                     "investment": st.column_config.ProgressColumn(
                         "Investment (USD)",
                         format="%f",
                         min_value=0,
                         max_value=max(df_selected_year_sorted.investment),
                     )}
                 )

    with st.expander('About', expanded=True):
        st.write('''
            - Data: [Our World Data](<https://ourworldindata.org/grapher/private-investment-in-artificial-intelligence?tab=table>).
            ''')
