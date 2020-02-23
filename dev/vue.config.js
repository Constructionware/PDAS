let path = require('path')

module.exports = {
 	outputDir: path.resolve(__dirname, '../templates'),
	assetsDir: 'static',
	indexPath: path.resolve(__dirname, '../templates/index.html'),
	publicPath: '/',
	productionSourceMap: true

}
