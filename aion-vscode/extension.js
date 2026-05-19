// =============================================================
// AION Language — VS Code Extension Entry Point
// =============================================================
// This file activates the AION VS Code extension.
// Syntax highlighting is handled by the tmLanguage grammar.
// This file adds extra features like commands and snippets.

const vscode = require('vscode');

function activate(context) {
    console.log('AION Language extension activated!');

    // ── Register AION Run command ─────────────────────────
    let runCommand = vscode.commands.registerCommand(
        'aion.runFile',
        function() {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage(
                    'No active AION file to run.');
                return;
            }

            const filepath = editor.document.fileName;
            if (!filepath.endsWith('.aion')) {
                vscode.window.showErrorMessage(
                    'This is not an AION file.');
                return;
            }

            // Run in terminal
            const terminal = vscode.window.createTerminal(
                'AION');
            terminal.show();
            terminal.sendText(
                `python main.py "${filepath}"`);
        }
    );

    // ── Register AION REPL command ────────────────────────
    let replCommand = vscode.commands.registerCommand(
        'aion.openRepl',
        function() {
            const terminal = vscode.window.createTerminal(
                'AION REPL');
            terminal.show();
            terminal.sendText('python main.py repl');
        }
    );

    // ── Status bar item ───────────────────────────────────
    const statusBar = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left, 100);
    statusBar.text = '$(zap) AION';
    statusBar.tooltip = 'AION Language v1.0.0';
    statusBar.command = 'aion.runFile';

    // Show status bar for .aion files
    vscode.window.onDidChangeActiveTextEditor(editor => {
        if (editor &&
            editor.document.fileName.endsWith('.aion')) {
            statusBar.show();
        } else {
            statusBar.hide();
        }
    });

    context.subscriptions.push(
        runCommand,
        replCommand,
        statusBar
    );
}

function deactivate() {}

module.exports = { activate, deactivate };