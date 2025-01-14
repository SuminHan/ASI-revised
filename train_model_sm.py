from asi_sm.model import AttentionSpatialInterpolationModel as asi

class train:

    def __init__(self, sigma, learning_rate, batch_size, num_neuron, num_layers, size_embedded,
                 num_nearest_geo, num_nearest_eucli, id_dataset, label, graph_label, num_nearest,
                 epochs, validation_split, early_stopping, optimier, sequence, **kwargs):

        """

        :param sigma:
        :param learning_rate:
        :param batch_size:
        :param num_neuron:
        :param num_layers:
        :param size_embedded:
        :param num_nearest_geo:
        :param num_nearest_eucli:
        :param id_dataset:
        :param label:
        :param graph_label:
        :param num_nearest:
        :param epochs:
        :param validation_split:
        :param early_stopping:
        :param optimier:
        :param kwargs:
        """

        self.NUM_NEAREST = num_nearest
        self.SIGMA = sigma
        self.LEARNING_RATE = learning_rate
        self.BATCH_SIZE = batch_size
        self.NUM_NEURON = num_neuron
        self.NUM_LAYERS = num_layers
        self.SIZE_EMBEDDED = size_embedded
        self.NUM_NEAREST_GEO = num_nearest_geo
        self.NUM_NEAREST_EUCLI = num_nearest_eucli
        self.ID_DATASET = id_dataset
        self.EPOCHS = epochs
        self.OPTIMIZER = optimier
        self.VALIDATION_SPLIT = validation_split
        self.LABEL = label
        self.EARLY_STOPPING = early_stopping
        self.GRAPH_LABEL = graph_label
        self.sequence = sequence


    def __call__(self):

        ####################################### Model ##########################################

        # build of the object
        spatial = asi(id_dataset=self.ID_DATASET,
                      num_nearest=self.NUM_NEAREST,
                      early_stopping=self.EARLY_STOPPING,
                      sequence = self.sequence
                      )

        # build of the model
        model = spatial.build(sigma=[0, self.SIGMA],
                              optimizer=self.OPTIMIZER,
                              learning_rate=self.LEARNING_RATE,
                              num_layers=self.NUM_LAYERS,
                              num_neuron=self.NUM_NEURON,
                              size_embedded=self.SIZE_EMBEDDED,
                              graph_label=self.GRAPH_LABEL,
                              num_nearest_geo=self.NUM_NEAREST_GEO,
                              num_nearest_eucli=self.NUM_NEAREST_EUCLI)

        # save architecture image
        spatial.architecture(model, 'architecture_'+self.LABEL)


        # fitt of the model
        weight, fit = spatial.train(model=model,
                                    epochs=self.EPOCHS,
                                    batch_size=self.BATCH_SIZE,
                                    validation_split=self.VALIDATION_SPLIT,
                                    label=self.LABEL,
                                    num_nearest_geo=self.NUM_NEAREST_GEO,
                                    num_nearest_eucli=self.NUM_NEAREST_EUCLI)

        # prediction
        result = spatial.predict_value(model=model,
                                       weights=weight,
                                       num_nearest_geo=self.NUM_NEAREST_GEO,
                                       num_nearest_eucli=self.NUM_NEAREST_EUCLI)


        ############################ Feature Extraction ###########################################
        DATA_TRAIN = ([spatial.X_train,
                       spatial.train_x_d[:, :self.NUM_NEAREST_GEO, :],
                       spatial.train_x_p[:, :self.NUM_NEAREST_EUCLI, :],
                       spatial.train_x_g[:, :self.NUM_NEAREST_GEO],
                       spatial.train_x_e[:, :self.NUM_NEAREST_EUCLI],
                       spatial.train_x_gn2v[:, :self.NUM_NEAREST_GEO+1],
                       spatial.train_x_en2v[:, :self.NUM_NEAREST_EUCLI+1]]
        )

        DATA_TEST = ([spatial.X_test,
                      spatial.test_x_d[:, :self.NUM_NEAREST_GEO, :],
                      spatial.test_x_p[:, :self.NUM_NEAREST_EUCLI, :],
                      spatial.test_x_g[:, :self.NUM_NEAREST_GEO],
                      spatial.test_x_e[:, :self.NUM_NEAREST_EUCLI],
                      spatial.test_x_gn2v[:, :self.NUM_NEAREST_GEO+1],
                      spatial.test_x_en2v[:, :self.NUM_NEAREST_EUCLI+1]]
        )

        #Embedded
        embedded_train = spatial.output_layer(model=model,
                                              weight=weight,
                                              layer='embedded',
                                              data=DATA_TRAIN,
                                              batch=self.BATCH_SIZE,
                                              file_name=self.ID_DATASET + '_embedded_train')
        embedded_test = spatial.output_layer(model=model,
                                             weight=weight,
                                             layer='embedded',
                                             data=DATA_TEST,
                                             batch=self.BATCH_SIZE,
                                             file_name=self.ID_DATASET + '_embedded_test')

        #Regression
        predict_regression_train = spatial.output_layer(model=model,
                                                        weight=weight,
                                                        layer='main_output',
                                                        data=DATA_TRAIN,
                                                        batch=self.BATCH_SIZE,
                                                        file_name=self.ID_DATASET + '_predict_regression_train')

        predict_regression_test = spatial.output_layer(model=model,
                                                       weight=weight,
                                                       layer='main_output',
                                                       data=DATA_TEST,
                                                       batch=self.BATCH_SIZE,
                                                       file_name=self.ID_DATASET + '_predict_regression_test')

        return spatial, result, fit, embedded_train, embedded_test, predict_regression_train, predict_regression_test