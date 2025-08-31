import dsr_node
# ---------------------------------------------------------------------------------------------------------------
#  Create data for train NN
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    for xx in range(300):
        cur_net = dsr_node.nets_mesh()
        cur_net.create_net()
        cur_net.impact_REB()


        cur_net.create_data_to_nn()
        cur_net.save_file_to_disc( file_name= r'd:\Sychov\HNUPS\Projects\DSR_data\train_snr_data.csv')


    for xx in range(100):
        cur_net = dsr_node.nets_mesh()
        cur_net.create_net()
        cur_net.impact_REB()


        cur_net.create_data_to_nn()
        cur_net.save_file_to_disc( file_name= r'd:\Sychov\HNUPS\Projects\DSR_data\test_snr_data.csv')

    for xx in range(100):
        cur_net = dsr_node.nets_mesh()
        cur_net.create_net()
        cur_net.impact_REB()


        cur_net.create_data_to_nn()
        cur_net.save_file_to_disc( file_name= r'd:\Sychov\HNUPS\Projects\DSR_data\valid_snr_data.csv')
