import easyocr as ocr # Optical Character Reader
import streamlit as st  # Web App
from PIL import Image, ImageEnhance , ImageFilter , ImageOps # Image Processing - Pillow
import pandas as pd
import numpy as np
import mysql.connector

def readImage(image_read):
    result=reader.readtext(image_read)    
    
    result_text = []  #Initializing a list to store the read texts

    for text in result: 
        result_text.append(text[1])
    
    df = pd.DataFrame.from_dict(result_text)

    return result_text
    
# To convert image to Binary File 
def convertToBinary(filename):
    with open(filename,'rb') as file:
        binarydata = file.read()
    return binarydata

# To convert Binary File to Image
def convertToFile(binarydata, filename):
    with open(filename,'wb') as file:
        file.write(binarydata)
        file.close()

st.title("Bizcard Reading using EasyOCR")
st.markdown("Using 'easyocr','streamlit', 'MySQL' ")
reader=ocr.Reader(['en'])

with st.container():

    image = st.empty()

    #st.subheader("Upload the image here")
    image = st.file_uploader(label= 'Upload your image here', type=['jpg','png','jpeg'], key = 'image')
    
    submit = st.button(label = 'Submit')

    if image:
    
        if "submit_state" not in st.session_state:
            st.session_state.submit_state = False
        
        if submit or st.session_state.submit_state:
            st.session_state.submit_state = True
        
        #if submit:
            input_image=Image.open(image)  # Read the image
            input_image.save(r"C:\Users\kgeet\OneDrive\Desktop\StreamlitImage.jpg") # Save the image locally
            #st.image(input_image)   #Display the image

            st.subheader("Choose any of the edited image below to display")

            # Cropping the image:
            cropped_image = input_image.crop(box = (100,10,650,302))
            if st.checkbox("Cropped Image"):
               st.image(cropped_image)

            # Re-sizing the image:
            #resiz_img=input_image.resize((700,600))
            resiz_img=cropped_image.resize((700,600))
            if st.checkbox("Resized Image"):
                st.image(resiz_img)

            # gray scaling:
            gray_image = ImageOps.grayscale(resiz_img)
            
            # Improving the constrast:
            enhanced_image=ImageEnhance.Contrast(gray_image)
            Contrast_image = enhanced_image.enhance(12)
            if st.checkbox("Enhanced Image"):
                st.image(Contrast_image)

            # Thresholding - image is catogorized into two classes - above and below threshold:
            threshold = 125
            threshold_image = Contrast_image.point(lambda p : p > threshold and 255 )
            if st.checkbox("Thresholded Image"):
                st.image(threshold_image)   

            # Sharpening the image:
            sharp_image = ImageEnhance.Sharpness(Contrast_image)
            sharpened_image = sharp_image.enhance(12)
            if st.checkbox("Sharpened Image"):
                st.image(sharpened_image)
                    
            st.subheader("To display the text from image, Click below")
            #if st.checkbox("Display Details"):


            display = st.button("Display Details",key = 1)
            # upload = st.button("Upload to DB", key = 2)  

            #Initialize Session_state:
            if "display_state" not in st.session_state:
                st.session_state.display_state = False
            
            if display or st.session_state.display_state:
                st.session_state.display_state = True

                with st.spinner("Reading...!"):

                    readtext_df = readImage(np.array(Contrast_image))
                    
                    df = pd.DataFrame.from_dict(readtext_df)

                    # Editing dataframe to display needed info
                    df_head = df.rename({0:'Bizcard Details'},axis = 1)
                    df_rows = df_head.rename({0:'Name', 1:'Profession', 2: 'Studio Name', 5: 'Address', 6 :'Ph-no' , 7 : 'E-mail'},axis = 0)
                    df_rows_edited = df_rows.drop([3,4,8,9,10,11],axis=0)

                    #st.dataframe(df)
                    st.dataframe(df_rows_edited)

                    #st.balloons()
                                        
                    #MYSQL Connection

                    #To display the extracted details:
                                                                
                    upload = st.button("Upload to DB")

                    # #Initialize Session_state:
                    # if "upload_state" not in st.session_state:
                    #     st.session_state.upload_state = False
                    
                    # if upload or st.session_state.upload_state:
                    #     st.session_state.upload_state = True
                    
                    if upload:

                        with st.spinner("Uploading...!"):

                            readtext_df = readImage(np.array(Contrast_image))

                            db_connect = mysql.connector.connect( host = 'localhost', user = 'root' , password = 'kgeetha@248' )

                            if db_connect.is_connected():
                                status = "Connection Established"
                            else:
                                status = "Connection Failed"
                                    
                            mycursor = db_connect.cursor(buffered = True)
                            
                            mycursor.execute("use mydb")
                                
                            #Create table in DB if not exists
                            mycursor.execute("CREATE TABLE IF NOT EXISTS bizcard_info(Id int AUTO_INCREMENT PRIMARY KEY, Name varchar(50),Profession varchar(50), studio varchar(50), Address varchar(50),Ph_number varchar(30),e_mail varchar(60),image blob)")
                            
                            ConvertPic = convertToBinary(r"C:\Users\kgeet\OneDrive\Desktop\StreamlitImage.jpg")
                                        
                            
                            # Insert Query    
                            query = '''INSERT INTO bizcard_info (Name, Profession, studio, Address, Ph_number,e_mail, image ) VALUES ( %s,%s,%s,%s,%s,%s,%s) '''
                            value = (readtext_df[0],readtext_df[1],readtext_df[2],readtext_df[5],readtext_df[6],readtext_df[7],ConvertPic)
                            #value = (result_text[0],result_text[1],result_text[2],result_text[5],result_text[6],result_text[7],ConvertPic)            
                            try:
                                            
                                mycursor.execute(query,value)
                                db_connect.commit()
                                print("Row Inserted")
                                st.success("Details Uploaded to Database")
                            except:
                                print("Insertion Failed")
                                st.error("Details not inserted")
                                
                            if db_connect.is_connected():
                                mycursor.close()
                                db_connect.close()
                                print("Connection is closed")   

    else:
        st.write("Please upload an image : {} ".format(" " .join(['jpg','png','jpeg'])))   


tab_titles = ["Retrieve Details" , "Update Details" , "Delete Record"]

tabs = st.tabs(tab_titles)

# column_2 , column_3 , column_4 = st.columns(3)

#Retriving from DB:
with tabs[0]:

    with st.form(key = "form_2", clear_on_submit = True):

        id_input = st.text_input("Enter the ID", key = 'id')
    
        retrieve = st.form_submit_button("Retrieve Details") 

        if "retrieve_state" not in st.session_state:
                st.session_state.retrieve_state = False
            
        if retrieve or st.session_state.retrieve_state:
                st.session_state.retrieve_state = True
            
                with st.spinner("Retrieving..!"):

                    if id_input:

                        db_connect = mysql.connector.connect(host = 'localhost', user = 'root' , password = 'kgeetha@248' )

                        if db_connect.is_connected():
                            print("Connection Established")
                        else:
                            print("Connection Failed")
                    
                        mycursor = db_connect.cursor(buffered = True)
                        mycursor.execute("use mydb")

                        query1 = '''SELECT Name, Profession, studio, Address, Ph_number,e_mail,id,image  FROM bizcard_info WHERE id = %s'''
                        value1 = (int(st.session_state["id"]),)

                        mycursor.execute(query1,value1)
                        data1=mycursor.fetchone()
                        
                        if data1:

                            ret_data = data1[:6]
                            ret_image = data1[7]   

                            print(ret_data)

                            ret_df = pd.DataFrame(ret_data)

                            # Editing dataframe to display needed info
                            ret_dfhead = ret_df.rename({0:'Bizcard Details'},axis = 1)
                            df_rows1 = ret_dfhead.rename({0:'Name', 1:'Profession', 2: 'Studio Name', 3: 'Address', 4 :'Ph-no' , 5 : 'E-mail', 6: 'ID'},axis = 0)
                            
                            st.dataframe(df_rows1)
                            
                            pic=convertToFile(ret_image, 'dwnld.jpg')                              
                        else:
                            st.error("Id not found")
                        
                        if db_connect.is_connected():
                                mycursor.close()
                                db_connect.close()
                                print("Connection is closed") 
            
# Update Database
with tabs[1]:
                                    
    update_id = st.text_input("Enter Id to update", key = "update_id") 
    
    update_field = st.selectbox("Enter the field to update", ['Name', 'Profession', 'Studio Name', 'Address','Ph_no','E_mail'], key = 'update_field')
    
    #with st.expander("Enter the value to update"):
        #name_updt = st.text_input("Enter the value to update", key = 'name_updt')
        
    update_value = st.text_input("Enter the details to update", key = 'update_value')

    update = st.button("Update")

    if "update_state" not in st.session_state:
        st.session_state.update_state = False
        
    if update or st.session_state.update_state:
        st.session_state.update_state = True

    if update:  

        db_connect = mysql.connector.connect( host = 'localhost', user = 'root' , password = 'kgeetha@248' )

        if db_connect.is_connected():
            print("Connection Established")
        else:
            print("Connection Failed")
        
        mycursor = db_connect.cursor(buffered = True)
        
        mycursor.execute("use mydb")
            
        # ConvertPic = convertToBinary(r"C:\Users\kgeet\OneDrive\Desktop\StreamlitImage.jpg")
        
        # Update Query
        
        if update_field == 'Name':
            query2 = ''' UPDATE bizcard_info SET Name = %s WHERE ID = %s'''

        if update_field == 'Profession':
            query2 = ''' UPDATE bizcard_info SET Profession = %s WHERE ID = %s'''

        if update_field == 'studio':
            query2 = ''' UPDATE bizcard_info SET studio = %s WHERE ID = %s''' 
        
        if update_field == 'Address':
            query2 = ''' UPDATE bizcard_info SET Address = %s WHERE ID = %s''' 

        if update_field == 'Ph_number':
            query2 = ''' UPDATE bizcard_info SET Ph_number = %s WHERE ID = %s''' 

        if update_field == 'e_mail,id':
            query2 = ''' UPDATE bizcard_info SET e_mail,id = %s WHERE ID = %s''' 

        #query2 = '''UPDATE bizcard_info SET Name = {update_value} WHERE id = {update_id} '''
        #query2 = ''' UPDATE bizcard_info SET %s = %s WHERE ID = %s'''
        value2 = (update_value,int(update_id))
        #value2 = (str(st.session_state["update_field"]),str(st.session_state["update_value"]),int(st.session_state["update_id"]))
        
        try:
            mycursor.execute(query2,value2)
            db_connect.commit()
            print("Row Updated")
            st.success("Details Updated in Database")
        except:
            print("Updation Failed")
            st.error("Details are not updated")

        query3 = '''SELECT Name, Profession, studio, Address, Ph_number,e_mail,id,image  FROM bizcard_info WHERE id = %s'''
        value3 = (int(update_id),)

        mycursor.execute(query3,value3)
        data1=mycursor.fetchone()
        
        if data1:

            ret_data = data1[:6]
            ret_image = data1[7]   

            print(ret_data)

            ret_df = pd.DataFrame(ret_data)

            # Editing dataframe to display needed info
            ret_dfhead = ret_df.rename({0:'Bizcard Details'},axis = 1)
            df_rows1 = ret_dfhead.rename({0:'Name', 1:'Profession', 2: 'Studio Name', 3: 'Address', 4 :'Ph-no' , 5 : 'E-mail', 6: 'ID'},axis = 0)
            
            st.dataframe(df_rows1)
            
            pic=convertToFile(ret_image, 'dwnld.jpg')      

        if db_connect.is_connected():
            mycursor.close()
            db_connect.close()
            print("Connection is closed")          

# Delete Record:
with tabs[2]:

    delete_id = st.text_input("Enter Id to delete", key = "delete_id")
                                        
    delete = st.button("Delete details")
    
    if delete:

        db_connect = mysql.connector.connect( host = 'localhost', user = 'root' , password = 'kgeetha@248' )

        if db_connect.is_connected():
            print("Connection Established")
        else:
            print("Connection Failed")
        
        mycursor = db_connect.cursor(buffered = True)
        
        mycursor.execute("use mydb")
        
        #Delete Query
        query4 = ''' DELETE FROM bizcard_info WHERE Id = %s'''
        value4 = (int(delete_id),)
        
        try:
            mycursor.execute(query4,value4)
            db_connect.commit()
            print("Record Deleted")
            st.success("Record deleted in Database")
        except:
            print("Delete Failed")
            st.error("Deletion Failed")
        
        if db_connect.is_connected():
            mycursor.close()
            db_connect.close()
            print("Connection is closed")

