from  adhoc_net import AdHocNet, save_gloabal_statistics
import os
import cv2

# ---------------------------------------------------------------------------------------------------------------
def run_research_pack_size():

    current_directory = os.getcwd()
    gloabal_history_list = []
    gloabal_statistics_list = []
    step_count = 10
    for itt in range(step_count):
        ad_hoc = AdHocNet()
        ad_hoc.flag_debug = True
        ad_hoc.create_net()
        ad_hoc.save_net_to_file(current_directory + r'\AdHoc_Net_research.xlsx')
        left_node = ad_hoc._get_node_from(xmin=0, xmax=150, ymin=ad_hoc._plase_y_size/2,
                                          ymax=ad_hoc._plase_y_size-10).node_id
        right_node = ad_hoc._get_node_from(xmin=ad_hoc._plase_x_size - 150, xmax=ad_hoc._plase_x_size - 2,
                                           ymin=ad_hoc._plase_y_size/2,ymax=ad_hoc._plase_y_size-10).node_id

        for message_size in range(1000,6000,2000):
            ad_hoc = AdHocNet()
            ad_hoc.flag_debug = True
            ad_hoc.load_net_from_file(file_name=current_directory + r'\AdHoc_Net_research.xlsx')
            ad_hoc.send_message(source_node_id=left_node, destination_node_id=right_node,
                                message_length=message_size)
            for i in range(200):
                ad_hoc.collect_debug_information()
                ad_hoc.turn_one_tik()
                ad_hoc.run_investigation()
                # print(i)
            gloabal_history_list = gloabal_history_list + ad_hoc.gloabal_history_list
            gloabal_statistics_list = gloabal_statistics_list + ad_hoc.gloabal_statistics_list
        print('\nStep  ' + str(itt+1) + ' // '+ str (step_count))

    save_gloabal_statistics(file_name=current_directory + r"\global.xlsx",
                            gloabal_history_list=gloabal_history_list,
                            gloabal_statistics_list=gloabal_statistics_list)


# ---------------------------------------------------------------------------------------------------------------
def run_debugs():
    ad_hoc = AdHocNet()
    ad_hoc.flag_debug = True
    current_directory = os.getcwd()
    # ad_hoc.create_net()
    # ad_hoc.save_net_to_file(current_directory + r'\AdHoc_Net_test.xlsx')
    ad_hoc.load_net_from_file(file_name=current_directory + r"\AdHoc_Net_test.xlsx")
    ad_hoc.show_net()
    ad_hoc.send_message(source_node_id=37, destination_node_id=23, message_length=1000)
    for i in range(200):
        ad_hoc.collect_debug_information()
        ad_hoc.turn_one_tik()
        ad_hoc.run_investigation()
    ad_hoc.show_net()

    ad_hoc.save_debug_information(file_name=current_directory + r"\debug.xlsx")
    ad_hoc.save_statistics_information(file_name=current_directory + r"\statistics.xlsx")
    save_gloabal_statistics(file_name=current_directory + r"\global.xlsx",
                            gloabal_history_list=ad_hoc.gloabal_history_list,
                            gloabal_statistics_list=ad_hoc.gloabal_statistics_list)


# ---------------------------------------------------------------------------------------------------------------
def run_random():
    ad_hoc = AdHocNet()
    ad_hoc.flag_debug = True
    current_directory = os.getcwd()
    ad_hoc.create_net()
    # ad_hoc.save_net_to_file(current_directory + r'\AdHoc_Net_test.xlsx')
    # ad_hoc.load_net_from_file(file_name=current_directory + r"\AdHoc_Net_test.xlsx")
    ad_hoc.show_net()
    left_node = ad_hoc._get_node_from(xmin=0, xmax=150, ymin=ad_hoc._plase_y_size / 2,
                                      ymax=ad_hoc._plase_y_size - 10).node_id
    right_node = ad_hoc._get_node_from(xmin=ad_hoc._plase_x_size - 150, xmax=ad_hoc._plase_x_size - 2,
                                       ymin=ad_hoc._plase_y_size / 2, ymax=ad_hoc._plase_y_size - 10).node_id
    ad_hoc.send_message(source_node_id=left_node, destination_node_id=right_node,
                        message_length=2000)
    for i in range(200):
        ad_hoc.collect_debug_information()
        ad_hoc.turn_one_tik()
        ad_hoc.run_investigation()
    ad_hoc.show_net()

    ad_hoc.save_debug_information(file_name=current_directory + r"\debug.xlsx")
    ad_hoc.save_statistics_information(file_name=current_directory + r"\statistics.xlsx")
    save_gloabal_statistics(file_name=current_directory + r"\global.xlsx",
                            gloabal_history_list=ad_hoc.gloabal_history_list,
                            gloabal_statistics_list=ad_hoc.gloabal_statistics_list)


# ---------------------------------------------------------------------------------------------------------------
def save_sample_generation(sub_dir, net_count):
    target_path = os.getcwd() + r'\\' + sub_dir
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    for index in range(net_count):
        ad_hoc = AdHocNet()
        ad_hoc.create_net()
        left_node = ad_hoc._get_node_from(xmin=0, xmax=150, ymin=ad_hoc._plase_y_size/2,
                                          ymax=ad_hoc._plase_y_size-10).node_id
        right_node = ad_hoc._get_node_from(xmin=ad_hoc._plase_x_size - 150, xmax=ad_hoc._plase_x_size - 2,
                                           ymin=ad_hoc._plase_y_size/2,ymax=ad_hoc._plase_y_size-10).node_id
        ad_hoc.save_net_to_file(target_path + r'\AdHoc_Net_' + str(index) + '.xlsx',
                                {'source_node':left_node, 'destination_node':right_node})
        image = ad_hoc.get_net_image()
        cv2.imwrite(target_path + r'\AdHoc_Net_' + str(index) + '.jpg', image)


# ---------------------------------------------------------------------------------------------------------------
def get_net_list(sub_dir):
    target_path = os.getcwd() + r'\\' + sub_dir
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    file_list = []
    for entry in os.listdir(target_path):
        full_path = os.path.join(target_path, entry)
        if os.path.isfile(full_path):
            if entry.find('.xlsx')>=0:
                file_list.append(full_path)
    return file_list


# ---------------------------------------------------------------------------------------------------------------
def run_pack_size_changes(sub_dir,runs_name,pack_size_list):
    current_directory = os.getcwd()
    file_list = get_net_list(sub_dir)
    for pk_size in pack_size_list:
        gloabal_history_list = []
        gloabal_statistics_list = []
        for file in file_list:
            print('\nPack size ' + str(pk_size) + '  ' + str(file_list.index(file) + 1) + ' // ' + str(len(file_list)))
            ad_hoc = AdHocNet()
            ad_hoc.flag_debug = True
            add_dic = ad_hoc.load_net_from_file(file)
            ad_hoc.send_message(source_node_id=add_dic['source_node'], destination_node_id=add_dic['destination_node'],
                                message_length=pk_size)
            for i in range(200):
                ad_hoc.collect_debug_information()
                ad_hoc.turn_one_tik()
                ad_hoc.run_investigation()

            gloabal_history_list = gloabal_history_list + [[file]] + ad_hoc.gloabal_history_list
            gloabal_statistics_list = gloabal_statistics_list + ad_hoc.gloabal_statistics_list



        save_gloabal_statistics(file_name=current_directory + r"\global" + runs_name + str(pk_size) + ".xlsx",
                                gloabal_history_list=gloabal_history_list,
                                gloabal_statistics_list=gloabal_statistics_list)

# ---------------------------------------------------------------------------------------------------------------
def run_ttl_size_changes(sub_dir,runs_name,pk_size: int, min_ttl: int, max_ttl:int = 0):
    current_directory = os.getcwd()
    file_list = get_net_list(sub_dir)
    for current_ttl in range(min_ttl, max(min_ttl, max_ttl) + 1):
        gloabal_history_list = []
        gloabal_statistics_list = []
        for file in file_list:
            print('\nTTL ' + str(current_ttl) + '  ' + str(file_list.index(file) + 1) + ' // ' + str(len(file_list)))
            ad_hoc = AdHocNet(ttl=current_ttl)
            ad_hoc.flag_debug = True
            add_dic = ad_hoc.load_net_from_file(file)
            ad_hoc.send_message(source_node_id=add_dic['source_node'], destination_node_id=add_dic['destination_node'],
                                message_length=pk_size)
            for i in range(200):
                ad_hoc.collect_debug_information()
                ad_hoc.turn_one_tik()
                ad_hoc.run_investigation()

            gloabal_history_list = gloabal_history_list + [[file]] + ad_hoc.gloabal_history_list
            gloabal_statistics_list = gloabal_statistics_list + ad_hoc.gloabal_statistics_list


            save_gloabal_statistics(file_name=current_directory + r"\global" + runs_name + str(current_ttl) + ".xlsx",
                                gloabal_history_list=gloabal_history_list,
                                gloabal_statistics_list=gloabal_statistics_list)

# ---------------------------------------------------------------------------------------------------------------
def save_jamm_changes(sub_dir,runs_name,jamm_list):
    current_directory = os.getcwd()
    file_list = get_net_list(sub_dir)
    for jamm in jamm_list:
        for file in file_list:
            print('\nJamm ' + str(jamm) + '  ' + str(file_list.index(file) + 1) + ' // ' + str(len(file_list)))
            ad_hoc = AdHocNet()
            ad_hoc.flag_debug = True
            add_dic = ad_hoc.load_net_from_file(file)
            ad_hoc.jamm_power = jamm
            ad_hoc.set_jamm_to_connects()
            ad_hoc.save_statistics_information(file_name=current_directory + r"\statistics  " +
                                                         runs_name+ str(jamm) + ".xlsx" )


# ---------------------------------------------------------------------------------------------------------------
def run_jamm_changes(sub_dir,runs_name,pk_size,jamm_list):
    current_directory = os.getcwd()
    file_list = get_net_list(sub_dir)
    for jamm in jamm_list:
        gloabal_history_list = []
        gloabal_statistics_list = []
        gloabal_log = []
        for file in file_list:
            print('\nJamm ' + str(jamm) + '  ' + str(file_list.index(file) + 1) + ' // ' + str(len(file_list)))
            ad_hoc = AdHocNet()
            ad_hoc.flag_debug = True
            add_dic = ad_hoc.load_net_from_file(file)
            ad_hoc.jamm_power = jamm
            ad_hoc.set_jamm_to_connects()
            ad_hoc.send_message(source_node_id=add_dic['source_node'], destination_node_id=add_dic['destination_node'],
                                message_length=pk_size)
            for i in range(200):
                ad_hoc.collect_debug_information()
                ad_hoc.turn_one_tik()
                ad_hoc.run_investigation()

            gloabal_history_list = gloabal_history_list + [[file]] + ad_hoc.gloabal_history_list
            gloabal_statistics_list = gloabal_statistics_list + ad_hoc.gloabal_statistics_list
            gloabal_log = gloabal_log + ad_hoc.log_path

        save_gloabal_statistics(file_name=current_directory + r"\global" + runs_name + str(jamm) + ".xlsx",
                                gloabal_history_list=gloabal_history_list,
                                gloabal_statistics_list=gloabal_statistics_list,gloabal_log=gloabal_log)

# ---------------------------------------------------------------------------------------------------------------
#  Run collect statistic for compare DSR and NN
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    # ad_hoc.run_debugs()
    # run_research_pack_size()
    # run_random()
    save_sample_generation(sub_dir='scenario_lbz_1', net_count=1)
    print(get_net_list(sub_dir='scenario_lbz_1'))
    save_sample_generation(sub_dir='ttl_long', net_count=25)
    print(get_net_list(sub_dir='ttl_long'))

    # run_pack_size_changes(sub_dir='scenario_lbz_1', runs_name='lbz1_p_size_',
    #                       pack_size_list=[13000])
    # run_ttl_size_changes(sub_dir='scenario_lbz_1', runs_name='lbz1_p_ttl_11_', pk_size=5000,
    #                      min_ttl=11)
    run_ttl_size_changes(sub_dir='ttl_long', runs_name='lbz1_p_ttl_', pk_size=5000,
                         min_ttl=7, max_ttl=20)

    # run_jamm_changes(sub_dir='scenario_lbz_1', runs_name='lbz1_p_jamm_with_snr', pk_size=5000,
    #                  jamm_list=[30000])
    # save_jamm_changes(sub_dir='scenario_lbz_1', runs_name='lbz1_jamm_with_snr',
    #                   jamm_list=[ 500, 300, 100 ])
