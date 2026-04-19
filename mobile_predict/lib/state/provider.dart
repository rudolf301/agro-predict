import 'package:flutter/widgets.dart';

import 'app_state.dart';

class AppStateProvider extends InheritedNotifier<AppState> {
  const AppStateProvider({
    super.key,
    required AppState state,
    required super.child,
  }) : super(notifier: state);

  static AppState of(BuildContext context, {bool listen = true}) {
    if (listen) {
      final widget =
          context.dependOnInheritedWidgetOfExactType<AppStateProvider>();
      assert(widget != null, 'AppStateProvider missing above this widget');
      return widget!.notifier!;
    }
    final widget = context
        .getInheritedWidgetOfExactType<AppStateProvider>();
    assert(widget != null, 'AppStateProvider missing above this widget');
    return widget!.notifier!;
  }
}
