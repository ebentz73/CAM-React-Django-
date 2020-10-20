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
          'css-loader'
        ]
      }
    ]
  }
};