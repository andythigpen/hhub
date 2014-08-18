(function() {

App.Models.Plugin = Backbone.Model.extend({
  defaults: {
    name: '',
    enabled: false
  }
});

App.Collections.PluginList = Backbone.Collection.extend({
  model: App.Models.Plugin
});

App.Views.PluginListView = Backbone.View.extend({
  el: '.plugin-list',
  initialize: function() {
    this.listenTo(this.collection, "change", this.render);
    this.listenTo(this.collection, "reset", this.render);
    this.render();
  },
  template: _.template($("#plugin-list-tmpl").html()),
  render: function() {
    this.$el.html(this.template({plugins: this.collection.models}));
    return this;
  }
});

App.plugins = new App.Collections.PluginList();
App.pluginsView = new App.Views.PluginListView({collection:App.plugins});

})();
