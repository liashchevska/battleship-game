module.exports = {
  devServer: {
    proxy: "http://localhost:8000"
  },
  css: {
    loaderOptions: {
      scss: {
        prependData: `@use "@/assets/scss/styles.scss";`
      }
    }
  }
};
