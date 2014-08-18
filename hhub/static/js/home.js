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
  events: {
    'change .checkbox': 'toggleEnable'
  },
  initialize: function() {
    this.listenTo(this.collection, "change", this.render);
    this.listenTo(this.collection, "reset", this.render);
    this.render();
  },
  template: _.template($("#plugin-list-tmpl").html()),
  render: function() {
    this.$el.html(this.template({plugins: this.collection.models}));
    return this;
  },
  toggleEnable: function(ev) {
    var model = this.collection.at($(ev.target).data('model-index'));
    model.set('enabled', ev.target.checked);
    model.save();
  }
});

App.plugins = new App.Collections.PluginList();
App.pluginsView = new App.Views.PluginListView({collection:App.plugins});

})();
