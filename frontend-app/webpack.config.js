let inCloud = ['dev', 'prod'].includes(process.env.DJANGO_ENV);

let azStorageAccount = process.env.AZ_STORAGE_ACCOUNT;
let azStorageHost = process.env.AZ_STORAGE_HOST === undefined ?
    `https://${azStorageAccount}.blob.core.windows.net` :
    process.env.AZ_STORAGE_HOST;
let azStaticContainer = process.env.AZ_STATIC_CONTAINER === undefined ?
    'static' : process.env.AZ_STATIC_CONTAINER;
let staticUrl = `${azStorageHost}/${azStaticContainer}/`;

module.exports = {
  entry: [
    './src'
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.css$/,
        exclude: /node_modules\/(?!(@fluentui|office-ui-fabric-react)\/).*/,
        use: [
          'style-loader',
          'css-loader',
        ]
      },
      {
        test: /\.(png|gif|jpe?g)$/,
        exclude: /node_modules/,
        loader: 'file-loader',
        options: {
          name (file) {
            return '[path][name].[ext]'
          },
          publicPath: function (url) {
            let path = url.replace('static/', inCloud ? staticUrl : 'http://localhost:8000/static/');
            return path;
          },
          outputPath: '../../'
        }
      }
    ]
  },
  resolve: {
    alias: {
      '/static/frontend-app': inCloud ? `${staticUrl}frontend-app/` : 'static/frontejnd-app'
    }
  }
};