
# 要件

* Google Authenticator で表示される６桁数字を出すアプリケーションを作成します。
* 複数のコードを同時に生成できるようにしたいです。機能はGoogle Authenticatorを参考にしたい


* インプットはQRコードであり、QRコードの解析結果は、以下のURLになります。以下の文字列以外は、形式が異なる旨を表示してほしい
  otpauth-migration://offline?data=[英数特殊記号文字列]

* 以下の手順でSecurityCodeを取得します。
  1. CLONE
    git clone https://github.com/dim13/otpauth
  2. Build Image
    docker build . -t otpauth:latest
  3. 実行
    docker run --name otpauth --rm otpauth:latest  -link "[Googleレンズで取得したotpahth URL]"
  4. 上記のOutput
    otpauth://totp/[Device名]@[アカウント名]?algorithm=SHA1&digits=6&issuer=[IssueName]&period=30&secret=[SecurityCode]

    SecurityCode の部分の文字列を使用する

* pythonライブラリpyotpを使用して、ワンタイムパスワードを生成する
  SecurityCodeには、上記のSecurityCode　を使用する

* 必要な機能は以下の２個
  * QRコードの読み込み、SecurityCodeの保管
    QRコードを読み込み、localファイルにSeritytyCodeを保管する。保管するファイルには複数のSecurityCodeを保管することができる
    QRコードの読み込みは、PCのカメラと連動をする
    このファイルはGitHubに連携をしてはいけない。
  * ワンタイムパスワードの表示
    コマンドを実行すると、登録されているSecurityCodeに対するワンタイムパスワードを表示させる。
    変更までにかかる秒数を表示して、毎秒更新をする
  * SecurityCodeの管理
    一覧、更新、削除を行うコマンドインターフェイスを用意する






