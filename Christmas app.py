import streamlit as st
import os
import psycopg2
#from dotenv import load_dotenv
import pandas as pd

# Load environment variables from the .env file
#load_dotenv()

class DatabaseActions():
    def __init__(self):
        self.dbname=os.getenv("DB_NAME")
        self.user=os.getenv("DB_USER")
        self.password=os.getenv("DB_PASSWORD")
        self.host=str(os.getenv("DB_HOST"))
        self.port=os.getenv("DB_PORT")

        self.url="postgresql://"+self.user+":"+self.password+"@"+self.host+".oregon-postgres.render.com/"+self.dbname

    def get_db_connection(self):
        conn = psycopg2.connect(
            #dbname=self.dbname,
            #user=self.user,
            #password=self.password,
            #host=self.url,
            #port=self.port
            self.url
        )
        return conn

    def get_table_contents(self, tbl_name):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = '''SELECT * FROM ''' + tbl_name
        cursor.execute(query)
        rows = cursor.fetchall()
        
        conn.commit()
        cursor.close()
        conn.close()
        return rows

    def insert_gift(self, person, gift_suggestor, gift_name, gift_url, bought_status, remove_status):
        # Establish a connection to the database
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Insert the new gift record into the table
        cursor.execute(
            """
            INSERT INTO gifts (person, gift_suggestor, gift_name, gift_url, bought_status, remove_status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (person, gift_suggestor, gift_name, gift_url, bought_status, remove_status)
        )

        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()

    def update_status(self, gift_id, status, status_type):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE gifts
            SET """ + status_type + """ = %s
            WHERE id = %s
            """

        cursor.execute(
            query,
            (status, gift_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

db = DatabaseActions()

data = db.get_table_contents("gifts")

# List of people
people = ["Gary", "Jesse", "Karyn", "Sam", "Yuliana"]

# Streamlit UI
st.title("Christmas Gift List Manager 🎁")

# User selects which person they are
user = st.selectbox("Who are you?", [""]+people)
gift_receiver = st.selectbox("Please select a person to shop for: ",people)

if user != "" and gift_receiver != None:
    
    st.write('---')
    st.subheader(f"Welcome, {user}! Please add a gift to {gift_receiver}'s list")

    left_col, right_col = st.columns(2)
    with left_col:
        gift_name = st.text_input("Gift Name", key=f"name_{gift_receiver}")
    with right_col:
        gift_url = st.text_input("Gift URL", key=f"url_{gift_receiver}")

    if st.button("Add gift to list"):
        if gift_name != "":
            db.insert_gift(gift_receiver, user, gift_name, gift_url, 'No', 'No')
            st.success("Gift added successfully!")
        else:
            st.write("You need to provide a gift name")


    st.write('---')
    st.subheader(f"Gift List for {gift_receiver}")

        # Fetch the gifts for the selected recipient
    gifts = db.get_table_contents("gifts")
    recipient_gifts = [gift for gift in gifts if gift[1] == gift_receiver and gift[6] != "Yes"]

    if user == gift_receiver:
        recipient_gifts = [gift for gift in gifts if gift[1] == gift_receiver]

    if recipient_gifts and user != gift_receiver:
        # Display a custom table layout with headers and checkboxes
        headers = ["ID", "Gift Suggestor", "Gift Name", "Gift URL", "Bought Status"]
        col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 3, 3, 2, 2])  # Adjust column sizes

        # Display headers
        col1.write("ID")
        col2.write("Gift Suggestor")
        col3.write("Gift Name")
        col4.write("Gift URL")
        col5.write("Bought")
        col6.write("Remove")

        # Checkboxes for updating the bought status
        bought_status_updates = {}
        remove_status_updates = {}
        for gift in recipient_gifts:
            gift_id, person, gift_suggestor, gift_name, gift_url, bought_status, remove_status = gift

            # Create columns for each row
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 3, 3, 2, 2])  # Adjust column sizes

            # Display each value in the respective column
            col1.write(gift_id)
            col2.write(gift_suggestor)
            col3.write(gift_name)
            col4.write(gift_url if gift_url else "N/A")

            # Checkbox for bought status
            bought_checkbox = col5.checkbox("Bought", value=(bought_status == "Yes"), key=f"bought_checkbox_{gift_id}")
            bought_status_updates[gift_id] = "Yes" if bought_checkbox else "No"
            
            remove_checkbox = col6.checkbox("Remove", value=(remove_status == "Yes"), key=f"remove_checkbox_{gift_id}")
            remove_status_updates[gift_id] = "Yes" if remove_checkbox else "No"

        if st.button("Update Status"):
            # Update the bought status in the database
            for gift_id, status in bought_status_updates.items():
                db.update_status(gift_id, status, "bought_status")
            for gift_id, status in remove_status_updates.items():
                db.update_status(gift_id, status, "remove_status")
            st.success("Gift statuses updated successfully!")

    elif recipient_gifts:
        # Display a custom table layout with headers and checkboxes
        headers = ["ID", "Gift Suggestor", "Gift Name", "Gift URL", "Bought Status"]
        col1, col2, col3, col4, col5 = st.columns([1, 2, 3, 3, 2])  # Adjust column sizes

        # Display headers
        col1.write("ID")
        col2.write("Gift Suggestor")
        col3.write("Gift Name")
        col4.write("Gift URL")
        col5.write("Remove")

        # Checkboxes for updating the bought status
        bought_status_updates = {}
        remove_status_updates = {}
        for gift in recipient_gifts:
            gift_id, person, gift_suggestor, gift_name, gift_url, bought_status, remove_status = gift

            # Create columns for each row
            col1, col2, col3, col4, col5 = st.columns([1, 2, 3, 3, 2])  # Adjust column sizes

            # Display each value in the respective column
            col1.write(gift_id)
            col2.write(gift_suggestor)
            col3.write(gift_name)
            col4.write(gift_url if gift_url else "N/A")
            
            remove_checkbox = col5.checkbox("Remove", value=(remove_status == "Yes"), key=f"remove_checkbox_{gift_id}")
            remove_status_updates[gift_id] = "Yes" if remove_checkbox else "No"

        if st.button("Update Status"):
            for gift_id, status in remove_status_updates.items():
                db.update_status(gift_id, status, "remove_status")
            st.success("Gift statuses updated successfully!")

    else:
        st.write("No gifts added for this person yet.")














    # if recipient_gifts:
    #     # Convert the recipient_gifts list into a DataFrame for a tabular display
    
    #     # Create a DataFrame
    #     columns = ["ID", "Person", "Gift Suggestor", "Gift Name", "Gift URL", "Bought Status"]
    #     gift_df = pd.DataFrame(recipient_gifts, columns=columns)
    #     gift_df.set_index("ID", inplace=True)

    #     # Display the DataFrame as a table
    #     st.table(gift_df)

    #     # Checkboxes for updating the bought status
    #     bought_status_updates = {}
    #     for gift in recipient_gifts:
    #         gift_id = gift[0]
    #         status = gift[5]
    #         checkbox = st.checkbox("Bought", value=(status == "Yes"), key=f"checkbox_{gift_id}")
    #         bought_status_updates[gift_id] = "Yes" if checkbox else "No"
        
    #     if st.button("Update Status"):
    #         # Update the bought status in the database
    #         for gift_id, status in bought_status_updates.items():
    #             db.update_bought_status(gift_id, status)
    #         st.success("Gift statuses updated successfully!")
    # else:
    #     st.write("No gifts added for this person yet.")










    # # Loop over all people and display lists except for the user's own
    # for person in people:
    #     if person != user:
    #         st.subheader(f"{person}'s Gift List")

    #         # Show the current list of gifts
    #         if gift_lists[person]:
    #             for i, gift in enumerate(gift_lists[person]):
    #                 st.write(f"{i + 1}. [{gift['name']}]({gift['url']})")
                
    #             # Option to remove a gift
    #             remove_index = st.number_input(f"Remove a gift from {person}'s list (enter number)", min_value=1, max_value=len(gift_lists[person]), step=1, key=f"remove_{person}")
    #             if st.button(f"Remove Gift from {person}'s List", key=f"remove_btn_{person}"):
    #                 gift_lists[person].pop(remove_index - 1)
    #                 save_gift_lists()
    #                 st.success(f"Gift removed from {person}'s list.")
    #         else:
    #             st.write("No gifts added yet.")

    #         # Input for adding a new gift
    #         gift_name = st.text_input(f"Gift Name for {person}", key=f"name_{person}")
    #         gift_url = st.text_input(f"Gift URL for {person}", key=f"url_{person}")
    #         if st.button(f"Add Gift to {person}'s List", key=f"add_{person}"):
    #             if gift_name and gift_url:
    #                 gift_lists[person].append({"name": gift_name, "url": gift_url})
    #                 save_gift_lists()
    #                 st.success(f"Gift added to {person}'s list.")
    #             else:
    #                 st.warning("Please provide both a gift name and URL.")

    # # Save the gift lists when Streamlit app is stopped
    # # save_gift_lists()
