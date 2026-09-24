class Textdiffedit < Formula
  desc "Review line edits before updating GitHub PR and issue bodies"
  homepage "https://github.com/s4na/textdiffedit"
  url "https://github.com/s4na/textdiffedit/archive/fba318cf114b5da9a8ff61eb4aa8e289826d1029.tar.gz"
  version "0.1.1"
  sha256 "a4763519033ff4afa3c40b0cf11dc20bfa8737b2168b33a6879109e736023f9a"
  head "https://github.com/s4na/textdiffedit.git", branch: "main"

  depends_on "gh"
  depends_on "python@3.11"

  def install
    libexec.install "textdiffedit"
    (bin/"textdiffedit").write <<~SH
      #!/bin/sh
      PYTHONPATH="#{libexec}${PYTHONPATH:+:$PYTHONPATH}" exec "#{Formula["python@3.11"].opt_bin}/python3.11" -m textdiffedit "$@"
    SH
    (bin/"textdiffedit").chmod 0755
  end

  test do
    assert_match "gh-pr-body", shell_output("#{bin}/textdiffedit --help")
  end
end
