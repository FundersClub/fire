var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var FaviconsWebpackPlugin = require('favicons-webpack-plugin');
var helpers = require('./helpers');

module.exports = {
    entry: {
        '1-polyfills': './src-frontend/polyfills.ts',
        '2-vendor': './src-frontend/vendor.ts',
        '3-app': './src-frontend/main.ts',
        'static': './src-frontend/static.ts'
    },

    resolve: {
        extensions: ['.ts', '.js']
    },

    module: {
        rules: [
            {
                test: /\.ts$/,
                loaders: ['awesome-typescript-loader', 'angular2-template-loader']
            },
            {
                test: /\.html$/,
                loader: 'html-loader'
            },
            {
                test: /\.(png|jpe?g|gif|svg|woff|woff2|ttf|eot|ico)$/,
                loader: 'file-loader?name=assets/[name].[hash].[ext]'
            },
            {
                test: /\.scss$/,
                include: helpers.root('src-frontend', 'app'),
                loaders: ['raw-loader', 'sass-loader']
            },
            {
                test: /\.css$/,
                exclude: helpers.root('src-frontend', 'app'),
                loader: ExtractTextPlugin.extract({
                    fallbackLoader: 'style-loader',
                    loader: 'css-loader?sourceMap'
                })
            },
            {
                test: /\.css$/,
                include: helpers.root('src-frontend', 'app'),
                loader: 'raw-loader'
            }
        ]
    },

    plugins: [
        // Workaround for angular/angular#11580
        new webpack.ContextReplacementPlugin(
            // The (\\|\/) piece accounts for path separators in *nix and Windows
            /angular(\\|\/)core(\\|\/)(esm(\\|\/)src|src)(\\|\/)linker/,
            helpers.root('./src-frontend'),
            {} // a map of your routes
        ),

        new HtmlWebpackPlugin({
            excludeChunks: ['static'],
            filename: 'app.html',
            template: 'src-frontend/index.html',
            // alphabetical order, so 1-polyfills is injected before 2-vendor, etc
            chunksSortMode: function (a, b) {
                if (a.names[0] > b.names[0]) {
                    return 1;
                }
                if (a.names[0] < b.names[0]) {
                    return -1;
                }
                return 0;
            }
        }),

        new HtmlWebpackPlugin({
            chunks: ['static'],
            filename: 'static.html',
            template: 'src-frontend/homepage.html'
        }),

        new FaviconsWebpackPlugin('./src-frontend/static/images/fire-favicon.png'),
    ]
};

