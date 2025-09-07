from  adhoc_net import AdHocNet, save_gloabal_statistics
import os

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
        left_node = ad_hoc._get_node_from(xmin=0, xmax=150).node_id
        right_node = ad_hoc._get_node_from(xmin=ad_hoc._plase_x_size - 150, xmax=ad_hoc._plase_x_size - 2).node_id

        for message_size in range(500,3000,500):
            ad_hoc = AdHocNet()
            ad_hoc.flag_debug = True
            ad_hoc.load_net_from_file(file_name=current_directory + r'\AdHoc_Net_research.xlsx')
            ad_hoc.send_message(source_node_id=left_node, destination_node_id=right_node,
                                message_length=message_size)
            for i in range(200):
                ad_hoc.collect_debug_information()
                ad_hoc.turn_one_tik()
                ad_hoc.run_investigation()
                print(i)
            gloabal_history_list = gloabal_history_list + ad_hoc.gloabal_history_list
            gloabal_statistics_list = gloabal_statistics_list + ad_hoc.gloabal_statistics_list
        print('\nStep  ' + str(itt) + ' // '+ str (step_count))

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
    # ad_hoc.send_message(source_node_id=37, destination_node_id=23, message_length=1000)
    # for i in range(200):
    #     ad_hoc.collect_debug_information()
    #     ad_hoc.turn_one_tik()
    #     ad_hoc.run_investigation()
    # ad_hoc.show_net()
    #
    # ad_hoc.save_debug_information(file_name=current_directory + r"\debug.xlsx")
    # ad_hoc.save_statistics_information(file_name=current_directory + r"\statistics.xlsx")
    # save_gloabal_statistics(file_name=current_directory + r"\global.xlsx",
    #                         gloabal_history_list=ad_hoc.gloabal_history_list,
    #                         gloabal_statistics_list=ad_hoc.gloabal_statistics_list)

# ---------------------------------------------------------------------------------------------------------------
#  Run collect statistic for compare DSR and NN
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    # ad_hoc.run_debugs()
    # run_research_pack_size()
    run_random()