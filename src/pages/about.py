import streamlit as st

import streamlit.components.v1 as components


def write():
    st.subheader("About")
    components.html(
        """
      <h3>Observation Mapper</h3>
      <body style="font-family: Verdana, sans-serif">
                Key words: GPS data logger,
                informal learning,
                citizen science,
                low cost,
                data privacy
                </br></br>

                More information on <a href='https://innodesign.io/tag/mapping/'>https://innodesign.io/tag/mapping/</a>
                </br></br>

                Development has been supported by the <b>SySTEM 2020 project</b>, 
                which has received funding from the European Union’s Horizon 2020 Research and Innovation Programme under Grant Agreement no. 788317
                </body>
      """, height=600, scrolling=True)
    st.balloons()


if __name__ == "__main__":
    write()
