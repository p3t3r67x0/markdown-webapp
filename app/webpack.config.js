const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MinifyPlugin = require('babel-minify-webpack-plugin')
const glob = require('glob')
const path = require('path')

const PATHS = {
  src: path.join(__dirname, 'src')
}

module.exports = {

  mode: process.env.NODE_ENV,
  entry: path.join(__dirname, 'src', 'index.js'),
  optimization: {
    minimizer: [new OptimizeCSSAssetsPlugin({})]
  },
  module: {
    rules: [{
      test: /\.js$/,
      exclude: /node_modules/,
      use: [{
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env']
        }
      }]
    }, {
      test: /\.html$/,
      use: [{
        loader: 'html-loader',
        options: {
          minimize: process.env.NODE_ENV === 'production'
        }
      }]
    }, {
      test: /\.(sa|sc|c)ss$/,
      use: [{
        loader: MiniCssExtractPlugin.loader,
        options: {
          hmr: process.env.NODE_ENV === 'development'
        }
      }, {
        loader: 'css-loader',
        options: {
          importLoaders: 1
        }
      }, {
        loader: 'postcss-loader'
      }]
    }, {
      test: /\.(png|svg|jpe?g|gif)$/,
      use: [{
        loader: 'file-loader',
        options: {
          outputPath: 'images'
        }
      }, {
        loader: 'image-webpack-loader',
        options: {
          mozjpeg: {
            progressive: true,
            quality: 65
          },
          optipng: {
            enabled: false,
          },
          pngquant: {
            quality: '65-90',
            speed: 4
          },
          gifsicle: {
            interlaced: false,
          },
          webp: {
            quality: 75
          }
        }
      }]
    }]
  },
  plugins: [
    new MinifyPlugin({}, {
      test: /\.js$/,
      sourceMap: process.env.NODE_ENV === 'development'
    }),
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: './src/index.html'
    }),
    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[hash].css'
    })
  ],

  devServer: {
    port: 3000,
    watchContentBase: true,
    contentBase: path.resolve(__dirname, 'src'),
    open: false,
  }
}
