from http import client
import time
from PIL import Image
import streamlit as st

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ws_blaster.manage import Manage
from ws_blaster.utils import save_uploadedfile, open_driver
from ws_blaster.blasting import Blaster

# Hide streamlit header and footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# INVOKE logo and WS logo setup
invoke_logo_path = '../ws-blaster-prod/images/invoke_logo.jpg'
ws_logo_path = '../ws-blaster-prod/images/ws-logo.png'
invoke_logo = Image.open(invoke_logo_path)
ws_logo = Image.open(ws_logo_path)
st.sidebar.title('Whatsapp Blaster')
st.sidebar.image(invoke_logo)
st.image(ws_logo)
option1 = st.sidebar.selectbox(
    'Select option', ('Blast Messages', 'Account Management'))


##############################################################
# Blasting
##############################################################
def main_blasting():
    blaster = Blaster(user_path="./Users")

    # Upload csv file to extract phone numbers
    uploaded_file = st.file_uploader(
        "Choose a file with phone numbers (csv)", type='csv')
    if uploaded_file is not None:
        blaster.extract_from_file(uploaded_file)
        col = st.selectbox('Select phone number column', blaster.columns)
        numbers = blaster.clean_numbers(col)
        st.json(blaster.contact_numbers_info)

    # Upload pictures
    if uploaded_file:
        uploaded_imgs = st.file_uploader(
            "Choose imgs you want to blast (png)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        blaster.save_files_to_blast(uploaded_imgs)

    # Variations of the same message
    if uploaded_file:
        message_variations = st.select_slider(
            "How many variations of the same message do you have?", options=list(range(1, 5)))
        for i in range(message_variations):
            message = st.text_area("Enter message: ", key=i)
            blaster.add_message_variations_to_blast(message)

    # Choose the set of platform to blast from
    if uploaded_file:
        platform = st.selectbox("Choose set of accounts to blast from",
                                ('Select', 'meniaga', 'AyuhMalaysia', "Burner Accounts"))
        if platform != 'Select':
            clients = blaster.get_clients(platform)
            client = st.selectbox("Choose client account", clients)

    # Start Blasting
    # TODO: Check if unavailable
    if uploaded_file and platform != "Select":
        start = st.button('Start Blasting')
        if start:
            st.info("Setting up Web Drivers")
            blaster.setup_drivers_in_account(platform, client)
            my_progress = st.progress(0.0)
            for i, number in enumerate(numbers):
                acc, driver = blaster.nav_to_number(number)
                message = blaster.get_random_message()
                if blaster.imgs:
                    status = blaster.send_file(driver)
                status = blaster.send_message(driver, message)
                my_progress.progress((i+1)/len(numbers))
                blaster.apply_random_wait(i)
            st.success("Messages sent to all numbers")
            blaster.close_drivers()


##############################################################
# Account Management
##############################################################

manage = Manage(user_path='./Users/', wsb_path='./Screenshot/')


def check_available_account():
    """
    Check available simcard registed in the apps.

    Available simcard is a registered simcard that still valid and not being banned.
    Not-available simcard is a registered simcard that have been banned.
    """
    st.markdown("----------------------------------------------")
    st.info("CHECK AVAILABLE simcard")
    # choose the platform
    select_platform = st.selectbox('Select set of simcard to check',
                                   ('',
                                    'meniaga',
                                    'AyuhMalaysia',
                                    'Burner Accounts'))

    #select_client = st.selectbox('Select client', manage.get_all_client_dir(select_platform))
    select_client = st.multiselect(
        'Select the Client(s):',  manage.get_all_client_dir(select_platform))
    if select_platform != '':

        if select_platform == 'Burner Accounts':
            select_platform = 'burner'

        # press the button to start CHECK
        button = st.button("CHECK")

        if button:
            with st.spinner('Checking simcard status...'):
                time.sleep(2)
                for client in select_client:
                    get_sim_list = manage.get_all_sim_name(
                        select_platform, client)
                    if len(get_sim_list) != 0:
                        st.header(f'👉 {client}')
                        check_all_acc_exist = manage.checking_banned_or_not(
                            get_sim_list, select_platform, client)

                        available = check_all_acc_exist[0]
                        not_available = check_all_acc_exist[1]

                        if len(available) == 0:
                            st.error('All sim(s) are not available!')
                        elif len(not_available) == 0:
                            st.success('All sim(s) are available!')
                            st.subheader('Available sim(s): ')
                            st.code('\n' + str(' | '.join(available)))
                        else:
                            st.success('Available sim(s): ')
                            st.code(str(' |  '.join(available)))
                            st.error('Unavailable sim(s): ')
                            st.code(str(' |  '.join(not_available)))
                    elif len(get_sim_list) == 0:
                        st.header(f'👉 {client}')
                        st.error(
                            'There is NO simcard registered for this client')


def add_new_client():
    st.markdown("----------------------------------------------")
    st.info("ADD NEW CLIENT")
    with st.form(key='new_client'):
        client_platform = st.selectbox('Choose platform for client',
                                       ('',
                                        'meniaga',
                                        'AyuhMalaysia',
                                        'Burner Accounts'))
        client_name = st.text_area("Enter client name:")
        button = st.form_submit_button("Add client")

    if button:
        with st.spinner("Adding new client..."):
            time.sleep(2)
            manage.add_client_directory(client_platform, client_name)

            st.success("{} sucessfully added!".format(client_name))


def add_new_account():
    """
    Adding new simcard. 

    How it works:
    1. Choose platform and new name. 
    2. Apps will produce a screenshot of the Whatsapp QR code.
    3. Scan the QR code using your mobile Whatsapp. 

    More:
    1. For every QR scan, a new simcard is created. 
    2. For every new name, even though it scanned by the same mobile, 
    it will create a new simcard. 
        Example: 
        new_name: Ammar_1 --> scanned by Ammar --> Ammar_1 simcard created
        new_name: Ammar_2 --> scanned by Ammar --> Ammar_2 simcard created
    3. QR code is refresh for every 15 seconds.
    """
    st.markdown("----------------------------------------------")
    st.info("ADD NEW simcard")
    select_platform_new_acc = st.selectbox('Where do you want to add the simcard(s)?',
                                           ('',
                                            'meniaga',
                                            'AyuhMalaysia',
                                            'Burner Accounts'))
    select_client = st.selectbox('Select Client', tuple(
        [' ', ]) + tuple(manage.get_all_client_dir(select_platform_new_acc)))
    # TODO: Adding client into open_driver

    if select_client != ' ':
        with st.form(key='new_simcard'):
            name = st.text_area("Enter Whatsapp simcard name:")
            get_name = manage.get_name(name)
            get_taken = manage.get_taken(
                name, select_platform_new_acc, select_client)

            send = st.form_submit_button('Add_simcard')

        if len(get_taken) == 0:
            if send:
                for name_acc in get_name:
                    st.subheader(f'⚠ {name_acc}: Please scan this QR code.')
                    try:

                        driver = manage.create_new_user_file(select_platform_new_acc,
                                                             select_client,
                                                             name_acc)
                        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                         '//*[@id="app"]/div/div/div[2]/div[1]/div/div[2]/div/canvas')))
                        manage.take_screenshot(driver)
                        st.success('QR code screenshot taken!')
                        manage.get_screenshot()

                        # wait until all cache file get
                        f = WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH,
                                                                                               '//*[@title="Search input textbox"]')))
                        st.success(name_acc + ' added!')
                        time.sleep(1)

                    except Exception as e1:
                        print('E1 ERROR:', e1)
                        #manage.deleted_account(select_platform_new_acc, select_client, name_acc)
                        st.error('ERROR: Whatsapp failed to link the simcard.')
        elif len(get_taken) == 1:
            st.error('Simcard name--' +
                     str(get_taken[0]) + ' has been existed. Try choose another name.')
        else:
            st.error(str(', '.join(get_taken)) +
                     ' are not available. Please choose another name!')


def deleting_account():
    """
    To delete NOT-AVAILABLE simcard only.
    Not-available simcard is banned simcard.
    """
    st.markdown("----------------------------------------------")
    st.info("DELETING ACCOUNT")

    select_platform = st.selectbox('Select platform',
                                   ('',
                                    'meniaga',
                                    'AyuhMalaysia',
                                    'burner'))

    select_client = st.selectbox('Select client', tuple(
        [' ', ]) + tuple(manage.get_all_client_dir(select_platform)))

    empty_list = []
    if select_platform != '' and select_client != ' ':
        get_sim_list = manage.get_all_sim_name(select_platform, select_client)
        # with st.spinner('Checking all simcard...'):
        # time.sleep(2)

        if len(get_sim_list) != 0:
            st.subheader(f'Working on {select_client} client')
            accs = manage.get_all_sim_name(select_platform, select_client)
            st.subheader('List of simcard: ')
            st.code(' | '.join(accs))

            st.subheader('Checking banned simcard...')
            bar = st.progress(0)
            for percent_complete in range(100):
                bar.progress(percent_complete+20)
                not_available_simcard = manage.checking_banned_or_not(
                    accs, select_platform, select_client)[1]
                bar.progress(percent_complete+50)
                empty_list.append(not_available_simcard)
                bar.progress(percent_complete+100)
                break

            unavailable = [z for x in empty_list for z in x]

            if len(empty_list) != 0:
                if len(unavailable) == 0:
                    st.success(
                        'All simcard is valid! \n No simcard need to be to deleted!')
                elif len(unavailable) > 0:
                    st.error('Unavailable simcard:')
                    st.code('\n' + ' | '.join(unavailable))

            unav = [k for x in empty_list for k in x]
            if len(unav) > 0:
                st.subheader(
                    'Click Delete if you confirm to delete the simcard.')
                approval_button = st.button('Delete')
                if approval_button:
                    for item in unav:
                        manage.deleted_account(
                            select_platform, select_client, item)
                        st.warning(f"{item} simcard has been deleted")
        elif len(get_sim_list) == 0:
            st.subheader(f'Working on {select_client} client')
            st.error('There is no simcard registered on this client.')


def user_learning():
    with st.container():
        """
        Tutorial for user.
        """
        st.title("Terms Used")
        st.markdown(
            """
                ### 👉 Platform
                > The product that we use to execute the blasting. 

                    Example: Decoris, Meniaga, Ayuh Malaysia
                """)

        st.markdown(
            """
                ### 👉 Client
                > Client that used WhatApp Blaster service

                    Example: Mc Donald, Restauran Maju
                
                """
        )
        st.markdown(
            """
                ### 👉 Simcard account
                > The sim card name that have been registered for the platform chosen by the client.

                > For every client, they have 3 simcard that can be used.

                    Example:  011-123 4567
                
                """)

        st.markdown(
            """
            ### ✅ Full-path
            > Format
                Platform > Client > Simcard account
            > Example:  
                Meniaga > Restauran Maju > 011- 123 4567
            """
        )
        st.title("Steps")
        st.markdown(
            """
            ### How to setup a new simcard for new client?

                1. Add new client name on "Add client name" section
                2. Move to "Add new simcard(s)
                3. Choose the platform of the client. 
                4. Select client name that has been added previously. 
                5. Enter Whatsapp number a simcard.
                6. Click "Add simcard(s)" button.
            """
        )


def main_account_management():

    #choice = st.selectbox('Select option',('', 'Tutorial', 'simcard Setup'))
    tab1, tab2 = st.tabs(['⚡Tutorial', '⚙ Simcard Settings'])

    # if choice == "Tutorial":
    with tab1:
        user_learning()

    # elif choice == "simcard Setup":
    with tab2:
        select_option = st.selectbox('Select what do you want to do?',
                                     ('',
                                      'Add new client',
                                         'Add new simcard',
                                      'Check available simcard',
                                         'Delete unavailable simcard'))

        if select_option == 'Add new client':
            add_new_client()

        elif select_option == 'Check available simcard':
            check_available_account()

        elif select_option == 'Add new simcard':
            add_new_account()

        elif select_option == 'Delete unavailable simcard':
            deleting_account()


if __name__ == '__main__':
    if option1 == 'Blast Messages':
        main_blasting()
    elif option1 == 'Account Management':
        main_account_management()
