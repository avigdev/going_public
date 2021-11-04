package {'emacs':
	ensure => present,
}

package {
	'git':
	ensure => present,
}

package {
	'mlocate':
	ensure => present,
}

package{
	'zsh':
	ensure => present,
}

package{
	'curl':
	ensure => present,
}


package{
	'nodejs':
	ensure => present,
}

package{'php':
	ensure => present,
}

package{'mysql-server':
	ensure => present,
}

package{'php-mysql':
	ensure => present,
}

package{'git-flow':
	ensure => present,
}

package{'npm':
	ensure => present,
}

package{'ack-grep':
	ensure => present,
}

package{'build-essential':
	ensure => present,
}

# python
package{'python3':
	ensure => present
}

package{'python3-distutils':
	ensure => present
}

package{'python3-venv':
	ensure => present

}
# stuff related to latex
package{'texlive-latex-base':
	ensure => present
}

package{'texlive-fonts-recommended':
	ensure => present
}

package{'texlive-fonts-extra':
	ensure => present
}

package{'texlive-latex-extra':
	ensure => present
}

package{'python3-pygments':
	ensure => present
}

package{'sqlite':
	ensure => present
}
