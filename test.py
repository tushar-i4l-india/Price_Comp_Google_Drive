import streamlit as st
import streamlit.components.v1 as components

from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import pandas as pd

df = pd.DataFrame({
    'Product': ['A', 'B', 'C'],
    'Brand': ['X', 'Y', 'Z'],
    'Price': [10, 20, 30],
    'Stock': [100, 200, 300]
})

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Product", pinned='left')
gb.configure_column("Brand", pinned='left')
grid_options = gb.build()

AgGrid(df, gridOptions=grid_options, height=200, width='100%')


components.html(
    """
    <html>
    <head>
    <style>
    .slider-wrapper {
        overflow: hidden;
        width: 100%;
        background: #f0f0f0;
        border-radius: 10px;
        margin: auto;
    }

    .slider-track {
        display: flex;
        width: calc(600px * 6); /* Adjust based on number of images * image width */
        animation: scroll 10s linear infinite;
    }

    .slide {
        flex-shrink: 0;
        width: 600px;
        margin: 10px;
        position: relative;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    .slide img {
        width: 100%;
        height: auto;
        border-radius: 10px;
        display: block;
    }

    .slide-title {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        padding: 10px;
        background: rgba(0, 0, 0, 0.6);
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
    }

    @keyframes scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); } /* Adjust to loop halfway if you duplicate slides */
    }
    </style>
    </head>
    <body>

    <div class="slider-wrapper">
        <div class="slider-track">
            <div class="slide">
                <div class="slide-title">Celotex</div>
                <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/walls_-_external_wall_insulation_-_timber_frame_walls_1.png?v=1737114043&width=1946">
            </div>
            <div class="slide">
                <div class="slide-title">Recticel</div>
                <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/Eurothane_20gp_11_1.jpg">
            </div>
            <div class="slide">
                <div class="slide-title">Ecotherm</div>
                <img src="https://build4less.co.uk/cdn/shop/files/Untitleddesign-2024-03-22T094324.755_64d98e44-6e84-46e8-8385-f6acb6837e9f.png?v=1711108001&width=1946">
            </div>
            <!-- Duplicate slides to ensure seamless looping -->
            <div class="slide">
                <div class="slide-title">Celotex</div>
                <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/walls_-_external_wall_insulation_-_timber_frame_walls_1.png?v=1737114043&width=1946">
            </div>
            <div class="slide">
                <div class="slide-title">Recticel</div>
                <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/Eurothane_20gp_11_1.jpg">
            </div>
            <div class="slide">
                <div class="slide-title">Ecotherm</div>
                <img src="https://build4less.co.uk/cdn/shop/files/Untitleddesign-2024-03-22T094324.755_64d98e44-6e84-46e8-8385-f6acb6837e9f.png?v=1711108001&width=1946">
            </div>
        </div>
    </div>

    </body>
    </html>
    """,
    height=600,
)
