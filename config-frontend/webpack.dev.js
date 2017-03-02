var webpackMerge = require('webpack-merge');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var commonConfig = require('./webpack.common.js');
var helpers = require('./helpers');

module.exports = webpackMerge(commonConfig, {
    devtool: 'cheap-module-eval-source-map',

    output: {
        path: helpers.root('dist-frontend'),
        publicPath: 'http://localhost:12001/',
        filename: '[name].js',
        chunkFilename: '[id].chunk.js'
    },

    plugins: [
        new ExtractTextPlugin('[name].css')
    ],

    devServer: {
        historyApiFallback: {
            verbose: true,
            rewrites: [
                // Send empty URL to homepage, all else to app.
                {
                    from: /^\/$/,
                    to: '/static.html'
                }, {
                    from: /^\/.+/,
                    to: '/app.html'
                }
            ]
        },
        stats: 'minimal',
        proxy: {
            '/{accounts,github,api,admin,static,media}/**': {
                target: 'http://localhost:12000',
                secure: false
            }
        }
    }
});
