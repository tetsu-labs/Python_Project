# Pythonジュニア教材：実装・検証ロードマップ

更新：2026-11-24。GitHub Issuesが無効のため、このファイルで進捗を管理します。

## 実装済み
- [x] 15章マニュアル
- [x] CSV集計CLI（テスト8件）
- [x] HTTPS JSONクライアント（テスト18件）
- [x] FastAPI + SQLite CRUD（テスト9件）
- [x] SQLite送金トランザクション（テスト12件）
- [x] pandas売上分析（テスト8件）
- [x] asyncio並列数制限（テスト5件）
- [x] ネットワーク障害ログ解析CLI（新規テスト14件、CI検証待ち）
- [x] GitHub ActionsにPython 3.12/3.13のpytest、Ruff、DockerビルドとHTTP疎通チェックを定義

## 検証の実績と限界
- **2026-11-24：手元にある教材一式でpytest 30 passed、compileall成功。** 対象はCRUD、CSV、pandas、asyncioの4演習。
- HTTPクライアント18件、SQLite送金12件は**以前のセッションで個別に成功した記録**があるが、今回のローカルZIPには含まれない。
- 全60件の同時実行は未確認。
- Ruffはこの実行環境で未導入。pipによる取得もネットワーク制限で失敗。
- Dockerコマンドがこの実行環境になく、ビルド・起動は未確認。
- GitHub Actionsはワークフローを更新したが、APIから実行成功を確認できていない。**設定済み≠成功確認済み**。

## 最優先：CI結果の確認
- 2026-11-24、ユーザー提供のGitHub Actions画面で #18（main、41秒）成功を確認。ただし個別ジョブ・テスト件数は画面から未確認。
- 障害ログ解析の新規テスト14件を追加したため、最新コミットでのCI再確認が必要。
1. [ ] [GitHub Actions](https://github.com/tetsu-labs/Python_Project/actions/workflows/python-junior-manual.yml)で最新コミットの実行を確認する。
2. [ ] 失敗があればログを取得して修正し、全60件とRuffとDockerの成功を確認する。
3. [ ] CIで成功したコミットSHAとテスト件数を記録する。

## 次に実装
4. [ ] HTTPクライアントのリダイレクト制限、Retry-After、総時間上限の強化
5. [ ] 認証付きAPIとPostgreSQLへの移行
6. [ ] OCR/MLの再現可能な実験
7. [ ] 総合課題、障害対応、レビュー・運用手順

完了条件：ソース、正常系・異常系テスト、README、再実行手順、検証結果の証跡。
